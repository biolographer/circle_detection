# -*- coding: utf-8 -*-
"""
Created on Wed Mar 19 12:21:46 2014

@author: Aaron Debon
"""
from __future__ import division
import matplotlib, sys
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pylab as plt
import cv2 
import numpy as np
import subprocess

if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk

from tkFileDialog import askdirectory
from tkSimpleDialog import askstring
from tkMessageBox import showinfo
param = [5., 200., 100., 140.]


root = Tk.Tk()
root.wm_title("O-detector")

root.image = np.empty([480, 640,3])


fig = plt.figure(figsize=(10,6))

im = plt.imshow(root.image) # later use a.set_data(new_data)
ax = plt.gca()
ax.set_xticklabels([]) 
ax.set_yticklabels([])

# a tk.DrawingArea
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.show()
canvas.get_tk_widget().pack(side=Tk.LEFT, fill=Tk.BOTH, expand = 1)



class hough:
    """ Circular Hough gui implementation for droplet measurement
     
     Author: Aaron Debon
     
     Parameters
     ----------
     c_size : maximum circle size to detect\n
     can_thr : threshold HoughCircles uses for canny edge detection\n
     h_thr : threshold HoughCircles uses for circle detection\n
     
     
     Instructions
     ------------
     Choose files: select folder with your data\n
     Left click : Left click on picture , draw and release creates a new circle.\n
     Right click : Removes circle that was clicked\n
     Blur : Gaussian blurs the image which is used to detect circles\n
     Detect : Hough circle detection\n
     Next : appends circles to final list and skips to next image\n
     
     Notes
     -----
     Circle detection based on Yuen, H. K. et al. Image Vision Comput. 8 1, pp 71–77 (1990)
     and Canny, J. IEEE Trans. on Pattern Analysis and Machine Intelligence, 
     8(6), pp. 679-698 (1986).
     
    """
    def __init__(self, c_size, can_thr, h_thr):
        ''' Initializes class for plotting, gui, image manipulation and 
        circle detection'''
        
        #parameter initialization        
        self.c_size = c_size
        self.can_thr = can_thr
        self.h_thr = h_thr
        self.thr_val = 140.0
        
        self.ig = np.empty(1)
        self.img0 = 1*root.image
        self.img_b = 1*root.image
        self.pic_count = 0
        self.result = []
        self.instr = Tk.StringVar()
    
    
        
        #Files  button
        Tk.Button(master = root, text = 'Choose Directory', 
                                command = self.files).pack(fill = Tk.X)
        
         #next  button
        Tk.Button(master = root, text = 'Next', 
                                command = self.next_b).pack(fill = Tk.X)
                                
        #previous  button
        Tk.Button(master = root, text = 'Previous', 
                                command = self.previous_b).pack(fill = Tk.X)
                        
    
        #detect button
        Tk.Button(master = root, text = 'Detect',
                                command = self.detect).pack(fill = Tk.X)
                                
        #draw button
        Tk.Button(master = root, text = 'Draw',
                                command = self.draw).pack(fill = Tk.X)
                                
        #reset button
        Tk.Button(master = root, text = 'Reset',
                                  command = self.reset).pack(fill = Tk.X)
        
        #blur button
        Tk.Button(master = root, text = 'Blur',
                                command = self.blur).pack(fill = Tk.X)
                                
        #save button
        Tk.Button(master = root, text="Save", 
                                command=self.save).pack(fill = Tk.X)

        #about  button
        Tk.Button(master = root, text = 'About', 
                                command = self.about).pack(fill = Tk.X)        
        
        #quit  button
        Tk.Button(master = root, text = 'Quit', 
                                command = self.quit_prog).pack(fill = Tk.X)
                                
        # Matplotlib mouse actions
        fig.canvas.mpl_connect('button_press_event', self.on_press)
        fig.canvas.mpl_connect('button_release_event',  self.on_release)
        
        label = Tk.Label( root, textvariable=self.instr, relief=Tk.RIDGE )
        label.pack(side = Tk.RIGHT, fill = Tk.X)
        self.instr.set("Choose your files")
       
    		
		
    def detect(self ):
        ''' detects circles using openCV hough transformation, returns only 
        circles that are completely inside the picture frame'''
        
        y_max, x_max = root.image.shape[:2]

        img = cv2.cvtColor(self.img_b, cv2.COLOR_BGR2GRAY)
      
        circ = cv2.HoughCircles(img, cv2.cv.CV_HOUGH_GRADIENT, 1, 
                                y_max/self.c_size, self.can_thr, 
                                self.h_thr, 5, 20)
        if circ != None:     
            self.circles = np.array([i for i in circ[0] 
                                 if i[::2].sum() <= x_max
                                 and i[0] - i[2] >= 0
                                 and i[1:3].sum() <= y_max
                                 and i[1] - i[2] >= 0]) 
        else:
            self.circles = np.array([])
            self.instr.set( 'No circles detected.')

                         
    def draw(self):
     	'''draws picture and circles if there are any''' 
     	
        root.image = 1*self.img0
        try:
            for i in self.circles:
                cv2.circle(root.image,(int(i[0]), int(i[1])), int(i[2]),(33,225,224),1)            
                cv2.circle(root.image,(int(i[0]), int(i[1])), 2,(43,255,255),3)
            im.set_data(root.image)
            canvas.draw()
        except:
            print 'first detect your circles'
        print 'circles drawn on root.image'

    def blur(self):
        self.img_b = cv2.medianBlur(self.img_b,5)
    
    def reset(self):
        self.img_b = 1*self.img0
        self.circles = np.array([])
        
    def on_press(self, event):
        '''mouse left click for coordinates. Mouse right detection and circle deletion'''
        
        self.x, self.y = event.xdata, event.ydata
        if event.button == 2:
            for i in self.circles:
                if event.xdata <= i[0]+i[2] and event.xdata >= i[0]- i[2] and event.ydata <= i[1]+i[2] and event.ydata >= i[1]- i[2]:                  
                    self.circles = self.circles[np.all(self.circles != i, axis = 1)]                 
            self.draw()
            
    def on_release(self, event):
        '''mouse left button release for circle drawing'''
        
        xr, yr = event.xdata, event.ydata
        if event.button == 1:
            x, y = self.x, self.y
            cx = x + 0.5*(xr - x)
            cy = y + 0.5*(yr - y)
            rad = 0.5*np.sqrt((xr-x)**2 + (yr-y)**2)
            try:
                self.circles = np.concatenate((self.circles,[[cx, cy, rad]]))
                self.draw()
            except:
                self.circles = np.array([[cx, cy, rad]])
                      
    def files(self):
    	''' generates list of files in folder and tries to filter compatible
    	files which it then reads in
    	 '''
        self.pics = 0
        self.pic_count = 0
        self.result = []
        self.wdir =  askdirectory()
        pic_temp = subprocess.check_output(['ls', self.wdir]).split('\n')
        print pic_temp
        ext = ['jpg','tif','bmp','jpeg','JPG','JPEG']
        self.pics = [i for i in pic_temp if i.split('.')[-1] in ext]
        
        try:        
            root.image = plt.imread(self.wdir+'/'+self.pics[0])
            self.img0 = 1*root.image
            self.img_b = 1*root.image
            im.set_data(root.image)
            canvas.draw()
            self.instr.set( 'detect and draw your circles. \nDraw with left, \ndelete with right mouse click')
        except:
            self.instr.set( 'no valid pictures, try converting to tif')
            
                        
    def next_b(self):
    	''' Skips to the next picture and appends circles from current pic in um'''
    	
        if self.pic_count < len(self.pics)-1:
            
            self.pic_count += 1
            self.instr.set('picture '+str(self.pic_count+1)+'/'+str(len(self.pics)))
            
            #appending circles from previous picture to result list in micro meters
            for i in self.circles:
                self.result.append(float(i[2]/1.423))             
            
            root.image = plt.imread(self.wdir+'/'+self.pics[self.pic_count])
            self.img0 = 1*root.image
            self.img_b = 1* root.image
            
            self.detect()
            self.draw()
            print 'append'
            
        elif self.pic_count == len(self.pics)-1:
            self.pic_count += 1
            for i in self.circles:
                self.result.append(float(i[2]/1.423))        
            print 'last apppend'
        else:
            print 'last picture'
        

    def previous_b(self):
        if self.pic_count > 0:
            self.pic_count -= 1
        root.image = plt.imread(self.wdir+'/'+self.pics[self.pic_count])
        self.img0 = 1*root.image
        self.img_b = 1* root.image
        self.draw()
        
    def save(self):
    	''' saves radii (um) and volumes (um^3)'''
    	
        var = askstring('Filename:', 'enter')
        print var
        out = open(self.wdir+'/'+var+'.txt','w')
        out.write('radius(um)'+'\t'+'volume(um^3)'+'\n')
        for i in self.result:
            if i > 42.5/2:
                vol = (i**2)*np.pi*42.5
            else:
                vol = (4/3.0)*np.pi*i**3
            out.write(str(i)+'\t'+str(vol)+'\n')
        out.close()
        self.instr.set('circles saved')
        
    def about(self):
        showinfo('About', 'Author: Aaron Debon\nQuestions and job offers to: adebon@ethz.ch')
    
    def quit_prog(self):
        print 'quit button press...'
        root.quit()     
        root.destroy() 
        

program = hough(param[0], param[1], param[2])


Tk.mainloop()


