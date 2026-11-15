import sys,glob
from PIL import Image, ImageDraw
fs=sorted(glob.glob(sys.argv[1]+'/f_*.jpg'),key=lambda f:float(f.split('_')[-1][:-4]))
n=len(fs); cols=2 if n<=4 else 3; rows=(n+cols-1)//cols; w=1920//cols; h=w*9//16
c=Image.new('RGB',(w*cols,h*rows))
for i,f in enumerate(fs):
    im=Image.open(f).resize((w,h)); ImageDraw.Draw(im).text((8,8),f.split('_')[-1][:-4],fill='yellow'); c.paste(im,((i%cols)*w,(i//cols)*h))
c.save(sys.argv[1]+'/hoja.jpg',quality=80)
