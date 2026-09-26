"""Shopify Agent — the first real (non-stub) agent.

Talks to the real Shopify Admin REST API. Read operations are considered
low-risk and are exposed directly. Write operations exist on this class too,
but nothing in this codebase calls them except the orchestrator's `_execute`
path, which only runs after PermissionManager + BudgetGuard + QA (+, for any
write, ApprovalQueue) all pass. The CEO never holds a reference to the
Shopify credentials or client directly (see `aicommerce.ceo.tools`) — it only
ever reaches this agent through `Orchestrator.run_cycle`.
"""
from __future__ import annotations

from typing import Optional

import requests

from aicommerce import config
from aicommerce.agents.base import Agent, AgentResult


class ShopifyNotConfigured(RuntimeError):
    pass


class ShopifyAgent(Agent):
    name = "shopify"

    READ_ACTIONS = {
        "read_products",
        "read_product",
        "read_inventory",
        "read_orders",
        "read_order",
        "read_customers",
        "read_shop",
    }
    WRITE_ACTIONS = {
        "create_product",
        "update_product",
        "set_price",
        "set_inventory",
        "delete_product",
    }

    def __init__(
        self,
        store: Optional[str] = None,
        token: Optional[str] = None,
        api_version: Optional[str] = None,
    ) -> None:
        self.store = store if store is not None else config.SHOPIFY_STORE
        self.token = token if token is not None else config.SHOPIFY_TOKEN
        self.api_version = api_version or config.SHOPIFY_API_VERSION

    @property
    def configured(self) -> bool:
        return bool(self.store) and bool(self.token)

    @property
    def operational(self) -> bool:
        """True only if real calls are actually possible: credentials present
        AND the profile permits external calls (not `offline`)."""
        return self.configured and config.PROFILE != "offline"

    def _base_url(self) -> str:
        return f"https://{self.store}/admin/api/{self.api_version}"

    def _headers(self) -> dict:
        return {"X-Shopify-Access-Token": self.token, "Content-Type": "application/json"}

    def _require_configured(self) -> None:
        if config.PROFILE == "offline":
            raise ShopifyNotConfigured(
                "PROFILE=offline: no real external calls are permitted in this profile, "
                "even though credentials may be present. Set PROFILE=sandbox or PROFILE=live "
                "in ai-commerce-os/.env to allow the Shopify agent to call the real API."
            )
        if not self.configured:
            raise ShopifyNotConfigured(
                "SHOPIFY_STORE / SHOPIFY_TOKEN are not set. Add them to ai-commerce-os/.env "
                "(see .env.example) to enable the Shopify agent."
            )

    def _get(self, path: str, params: Optional[dict] = None) -> dict:
        self._require_configured()
        r = requests.get(f"{self._base_url()}{path}", headers=self._headers(), params=params, timeout=15)
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, payload: dict) -> dict:
        self._require_configured()
        r = requests.post(f"{self._base_url()}{path}", headers=self._headers(), json=payload, timeout=20)
        r.raise_for_status()
        return r.json()

    def _put(self, path: str, payload: dict) -> dict:
        self._require_configured()
        r = requests.put(f"{self._base_url()}{path}", headers=self._headers(), json=payload, timeout=20)
        r.raise_for_status()
        return r.json()

    def _delete(self, path: str) -> None:
        self._require_configured()
        r = requests.delete(f"{self._base_url()}{path}", headers=self._headers(), timeout=15)
        r.raise_for_status()

    # ------------------------------------------------------------------
    # Agent protocol — dispatch by action name
    # ------------------------------------------------------------------
    def execute(self, task: dict) -> AgentResult:
        action = task.get("action")
        params = task.get("params", {})
        try:
            handler = getattr(self, f"_do_{action}", None)
            if handler is None:
                return AgentResult(success=False, error=f"unknown shopify action '{action}'")
            output = handler(**params)
            return AgentResult(
                success=True,
                output=output,
                evidence=f"shopify admin API call succeeded for action '{action}'",
            )
        except ShopifyNotConfigured as exc:
            return AgentResult(success=False, error=str(exc))
        except requests.HTTPError as exc:
            return AgentResult(success=False, error=f"Shopify API error: {exc}")
        except Exception as exc:  # noqa: BLE001 — surface as a failed AgentResult, not a crash
            return AgentResult(success=False, error=f"unexpected error calling Shopify: {exc}")

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------
    def _do_read_shop(self) -> dict:
        return self._get("/shop.json")["shop"]

    def _do_read_products(self, limit: int = 50, status: str = "any") -> list[dict]:
        return self._get("/products.json", {"limit": limit, "status": status}).get("products", [])

    def _do_read_product(self, product_id: int) -> Optional[dict]:
        return self._get(f"/products/{product_id}.json").get("product")

    def _do_read_inventory(self, inventory_item_ids: list[int]) -> list[dict]:
        ids = ",".join(str(i) for i in inventory_item_ids)
        return self._get("/inventory_levels.json", {"inventory_item_ids": ids}).get("inventory_levels", [])

    def _do_read_orders(self, status: str = "any", limit: int = 50) -> list[dict]:
        return self._get("/orders.json", {"status": status, "limit": limit}).get("orders", [])

    def _do_read_order(self, order_id: int) -> Optional[dict]:
        return self._get(f"/orders/{order_id}.json").get("order")

    def _do_read_customers(self, limit: int = 50) -> list[dict]:
        return self._get("/customers.json", {"limit": limit}).get("customers", [])

    # ------------------------------------------------------------------
    # Writes — only ever reached via Orchestrator.run_cycle (permission +
    # budget + QA + approval already happened by the time this runs)
    # ------------------------------------------------------------------
    def _do_create_product(self, product_data: dict) -> dict:
        return self._post("/products.json", {"product": product_data})["product"]

    def _do_update_product(self, product_id: int, updates: dict) -> dict:
        return self._put(f"/products/{product_id}.json", {"product": {"id": product_id, **updates}})["product"]

    def _do_set_price(self, variant_id: int, price: str) -> dict:
        return self._put(f"/variants/{variant_id}.json", {"variant": {"id": variant_id, "price": price}})["variant"]

    def _do_set_inventory(self, inventory_item_id: int, location_id: int, available: int) -> dict:
        return self._post(
            "/inventory_levels/set.json",
            {"location_id": location_id, "inventory_item_id": inventory_item_id, "available": available},
        )

    def _do_delete_product(self, product_id: int) -> None:
        self._delete(f"/products/{product_id}.json")
