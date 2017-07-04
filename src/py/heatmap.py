#
# twiddle with paths
#
import sys
sys.path.append("DLLs")

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

font_path="fonts/helvR08.pil"

class Heatmap:
    "Class to draw a heat map"

    def __init__(self):
        self.size    = (500,500)
        self.bgcolor = (255,255,255)
        self.data    = [ 
            [1,2,3], [4,5,6], [7,8,9],
            [1,2,3], [4,5,6], [7,8,9],
            [1,2,3], [4,5,6], [7,8,9]
        ]
        self.plotbox = (10,10,390,390)
        self.legendbox = (400,10, 490, 390)
        self.thumbsize=(100,100)
        self.ylabels=[]

    def calcdatarange(self):
        datamin=datamax=self.data[0][0]
        for row in self.data:
           rowmin=min(row)
           rowmax=max(row)
           datamin = min(datamin, rowmin)
           datamax = max(datamax, rowmax)
        self.datamax=datamax
        self.datamin=datamin
        self.datarange=datamax-datamin

    def draw_legend(self, image):
        "draws a legend on the image"
        #
        # Create a legend on another bitmap
        # set legend width, height
        #
        w = self.legendbox[2] - self.legendbox[0] 
        h = self.legendbox[3] - self.legendbox[1] 
        im_legend=Image.new("RGB", (w,h), (255,255,255))
        im_font=ImageFont.load(font_path)
        im_draw=ImageDraw.ImageDraw(im_legend)
        im_draw.setfont(im_font)
        #
        # Put a scale down the left hand side
        #
        x1=0
        for y in range(5, h, 20):
            value = self.datarange * float(h-y)/ float(h) + self.datamin
            text = "%5.3f" % value
            wt, ht = im_draw.textsize(text)
            im_draw.text((x1-wt,y-ht/2), text, fill=(0,0,0))
            x1 = max(wt,x1)
        #
        # Paint the legend
        #
        for y in range(h):
            value = self.datarange * float(h-y)/ float(h) + self.datamin
            im_draw.line([(x1+5,y),(w,y)], fill=self._heatcolor(value))
        #    
        # Transfer legend to a canvas
        #
        image.paste (im_legend, self.legendbox)

    def draw_xaxis(self, image):
        "draws x axis on the image"
        #
        # create a drawing object
        #
        im_font = ImageFont.load(font_path)
        im_draw = ImageDraw.ImageDraw(image)
        im_draw.setfont(im_font)
        #
        # draw a line
        #
        x1, y1, x2, y2 = self.plotbox
        im_draw.line([(x1, y2), (x2, y2)], (0,0,0))
        # 
        # draw text
        #
        sizex = len(self.data[0])

        for x in range(0, sizex, 10):
            #h,w=im_draw.textsize(str(x))
            im_draw.text((x1 + (x + 0.5) * (x2-x1) /sizex, y2), 
                str(x+1), fill=(0,0,0) )

    def plotsize(self):
        x1, y1, x2, y2 = self.plotbox
        return abs(x2-x1),abs(y2-y1)

    def setsize(self, x,y):
        "sets the canvas size"
        self.size= (x,y)

    def setdata(self, data):
        "sets the heat map matrix using a list of lists"
        self.data = data

    def setdatafile(self, filename):
        "reads a matrix of numbers from a given filename"
        lines=open(filename, 'r').readlines()
        import string
        self.data=map(string.split, lines)
        for i in range(len(self.data)):
           self.data[i]=map(float,self.data[i])

    def setplot( x1, y1, x2, y2):
        "sets the dimension of the plot box"
        self.plotbox = (x1, y1, x2, y2)

    def plot(self, out_filename, thumb_filename=""):
        "outputs a heat map to a file"

        # Calculate data range so that appropriate
        # colors can be assigned
        #
        self.calcdatarange()

        #
        # Plot heatmap on a matrix
        #
        sizex, sizey = len(self.data[0]), len(self.data)
        im_heat = Image.new('RGB', (sizex, sizey))
        for x in range(sizex):
          for y in range(sizey):
            value = self.data[y][x]
            color = self._heatcolor(value)

            # preferred style
            im_heat.putpixel( (x,y) , color)

            # matlab style
            #im_heat.putpixel( (x,sizey-y-1), color)

        #
        # Transfer heatmap to a canvas
        #
        im = Image.new( 'RGB', self.size, self.bgcolor)
        im.paste (im_heat.resize(self.plotsize()), self.plotbox)

        # 
        # Plot x axis, legend
        #
        self.draw_xaxis(im)
        self.draw_legend(im)

        im.save( out_filename)

        #
        # Save heatmap as a thumbnail
        #
        if thumb_filename:
          im_thumb=im_heat.resize(self.thumbsize)
          im_thumb.save( thumb_filename )

    def _heatcolor(self, scalar):
        "Returns a rgb tuple given a scalar"

        # transform scalar to valid range of
        # 0 - 1024
        t_scalar = (1024.0 * (scalar - self.datamin)) / self.datarange
        b=self._heatsub(t_scalar, 0    -128)
        g=self._heatsub(t_scalar, 256  -128)
        r=self._heatsub(t_scalar, 512  -128)
        return r,g,b

    def _heatsub(self, scalar, shift):
        normal = scalar - shift
        if normal < 256:
            pass
        elif normal < 512:
            normal = 255
        else:
            normal = 768 - normal
        if normal<0: normal=0
        if normal>255: normal=255
        return normal

class TransposedFont:

    def __init__(self, font, orientation=None):
        self.font = font
        self.orientation = orientation

    def getsize(self, text):
        w, h = self.font.getsize(text)
        if self.orientation in (Image.ROTATE_90, Image.ROTATE_270):
            return h, w
        return w, h

    def getmask(self, text):
        im = self.font.getmask(text)
        if self.orientation is not None:
            return im.transpose(self.orientation)
        return im

if __name__=='__main__':
    heatmap = Heatmap()
    heatmap.setdatafile('heatmap.cut')
    heatmap.plot('heatmap.png', 'heatmap_th.png')

# vi:ai:sw=3:sts=4:is:sw=4
