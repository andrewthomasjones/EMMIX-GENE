#
# heatmapsvg.py
#
# Draws SVG heat maps
#
# $Log: heatmapsvg.py,v $
# Revision 1.1  2002/09/22 05:33:48  default
# Plots SVG Heatmaps
# Added the Heatmap.ylabels attribute to plot gene labels
#
#
class Heatmap:

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

    def setdatafile(self, filename):
        "reads a matrix of numbers from a given filename"
        lines=open(filename, 'r').readlines()
        import string
        self.data=map(string.split, lines)
        for i in range(len(self.data)):
           self.data[i]=map(float,self.data[i])
           
    def draw_legend(self, image):
        "returns a svg output of a legend"
        w = self.legendbox[2] - self.legendbox[0] 
        h = self.legendbox[3] - self.legendbox[1] 
        #
        # Put a scale down the left hand side
        #
        x1=0
        for y in range(5, h, 20):
            value = self.datarange * float(h-y)/ float(h) + self.datamin
            text = "%5.3f" % value
            #wt, ht = im_draw.textsize(text)
            #im_draw.text((x1-wt,y-ht/2), text, fill=(0,0,0))
            #x1 = max(wt,x1)

        x1=5 # xxx
        #
        # Paint the legend
        #
        result =""
        for y in range(h):
            value = self.datarange * float(h-y)/ float(h) + self.datamin
            # im_draw.line([(x1+5,y),(w,y)], fill=self._heatcolor(value))
            result += """
        <line x1="%d" y1="%d" x2="%d" y2="%d" style="fill:none;stroke:#%s" />""" \
            % (x1+5, y, x1+5+w, y, self._heatrgb(*self._heatcolor(value)))

        return result

    def draw_yscale(self):
        "annotates the y-scale (gene names)"
        #
        # If annotation labels are available then
        # use them
        #
        if len(self.ylabels) > 0:
            result = []
            for y in range(len(self.ylabels)):
                label=self.ylabels[y]
                result.append ( """
        <text x="%d" y="%d" style="font-size:5px">%s</text>""" % \
        (0, y*5+5, label))
            return "\n".join(result)
        else:
            sizex, sizey = len(self.data[0]), len(self.data)
            result = ""
            for y in range(sizey):
                result += """
            <text x="%d" y="%d" style="font-size:5px">%s</text>""" % \
            (0, y*5+5, "GENE%03d" % y)
            return result
        
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
        svg_heat = ""
        for x in range(sizex):
          for y in range(sizey):
            value = self.data[y][x]
            color = self._heatrgb(*self._heatcolor(value))
            svg_heat += """
        <use xlink:href="#pixel_def" x="%d" y="%d" style="fill:#%s"/>""" \
        % (x*5,y*5,color)

        svg_legend = self.draw_legend(None)
        svg_yscale = self.draw_yscale()
        svg_plot = \
"""<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" 
  "http://www.w3.org/TR/SVG/DTD/svg10.dtd"
   [<!ATTLIST svg
      xmlns:xlink CDATA #FIXED "http://www.w3.org/1999/xlink">
   ]>
<svg xmlns="http://www.w3.org/2000/svg"
     enableZoomAndPanControls="true"
     contentScriptType="text/ecmascript"
     zoomAndPan="magnify"
     version="1.0"
     contentStyleType="text/css"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     onload="init(evt);">
     <script language="JavaScript"><![CDATA[
        function init(evt) {
            svgdoc=evt.getTarget().getOwnerDocument();
            textobj=svgdoc.getElementById('ytitle');
            textrect=textobj.getBBox();
            
            plotobj=svgdoc.getElementById('plot');
            plottransform='translate(' + (textrect.width+10).toString() + ',0)';
            plotobj.setAttribute("transform",plottransform);
            plotrect=plotobj.getBBox();

            legendobj=svgdoc.getElementById('legend');
            legendtransform='translate(' + (
                textrect.width + plotrect.width+10).toString() + ',0)';
            legendobj.setAttribute("transform",legendtransform)
            
        }
     ]]>
     </script>
     <defs>
       <g id="pixel_def">
        <rect x="0" y="0" width="4" height="4" 
         style="stroke-width:0.5;stroke:gray;" />
       </g>
     </defs>
     <g id="ytitle">
     %(svg_yscale)s
     </g>
     <g id="plot">
     %(svg_heat)s
     </g>
     <g id="legend">
       <g transform="scale(1,0.25)">
     %(svg_legend)s
       </g>
     </g>
</svg>     
""" % locals()

        open(out_filename,"w").write(svg_plot)

    def _heatrgb(self, r,g,b):
        temp = "%2s%2s%2s" % \
         (hex(int(r))[2:],hex(int(g))[2:],hex(int(b))[2:])
        return temp.replace(" ","0")

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

if __name__ == "__main__":
    heatmap = Heatmap()
    heatmap.setdatafile("heatmap.cut")
    heatmap.plot("heatmap.svg", "heatmap_th.svg")

