import cv2
#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg
import numpy as np
import time
import datetime
from Quality_Measure import *

class ContourOperations:
	def __init__(self):
		self.image=[]
		self.analyzedImage=[]
		self.box=[]
		self.contourlist=[]
		self.contoursorted=[]
		self.contour_to_show=[]
		self.sliceWidth=5
		self.contour_no=0
		self.dimX=0
		self.dimY=0
		self.object_threshold=100000000000
		self.image_threshold=0
		self.show_scale_factor=1.0
		self.OrientationStatus="UNKNOWN"
		self.SizeStatus="UNKNOWN"
		self.imageCounter=0
		self.deltaTime=0.0
		self.leadZeros=5
		self.controlImagePath='/tmp/'
		self.totalArea=0
	
	def set_save_path(self, path):
		self.controlImagePath=path
	
	def set_contour_no(self, contour_no):
		self.contour_no=contour_no
	
	def set_slice_width(self, width):
		self.sliceWidth=width
	
	def list_contours(self):
		if self.dimX>0:
			(cnts, _) = cv2.findContours(self.image, cv2.RETR_EXTERNAL, self.contourApprox)
			#(cnts, _) = cv2.findContours(self.image, cv2.RETR_TREE, 1)
			#CHAIN_APPROX_SIMPLE CV_CHAIN_APPROX_TC89_L1,CV_CHAIN_APPROX_TC89_KCOS
			#cv::CHAIN_APPROX_NONE = 1,   cv::CHAIN_APPROX_SIMPLE = 2,  cv::CHAIN_APPROX_TC89_L1 = 3,  cv::CHAIN_APPROX_TC89_KCOS = 4
			
			cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
			self.contoursorted=cnts
		
	def get_selected_contour(self):
		self.list_contours()
		if len(self.contoursorted)>0:
			self.contour_to_show=self.contoursorted[self.contour_no]
			#del contour_to_show[0]
			#print("showcontour")
			return self.contour_to_show
		else: 
			#print("no contour!")
			return None  
			
	def set_object_threshold(self, threshold):
		self.object_threshold=threshold
	
	def set_image_threshold(self, threshold):
		self.image_threshold=threshold
	
	def compute_image(self,frame):
		self.dimX , self.dimY = frame.shape[:2]
		if self.dimX>0:
			self.grayImage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			ret, thresh = cv2.threshold(self.grayImage,self.image_threshold,255,0)
			self.image=thresh
			self.image_orig=self.image.copy()
		#cv2.imshow('Test',self.image)
	
	def showPreview(self, show_raw, show_computed):
		if show_raw==True and show_computed==False and self.dimX>0:
			cv2.imshow('Threshold',self.image_orig)
			cv2.imshow('Grayscale',self.grayImage)
		elif show_computed==True and len(self.box)>0:
			if self.analyzedImage is not None :
				if len(self.analyzedImage)>0:
					cv2.imshow('Result',self.analyzedImage)
			else:
				img_box=cv2.cvtColor(self.image_orig, cv2.COLOR_GRAY2BGR)
				box = cv2.cv.BoxPoints(self.box) 
				box = np.array(box, dtype="int")
				cv2.drawContours(img_box, [box], -1, (255, 0, 0), 2)
				cv2.drawContours(img_box, self.contour_to_show, -1, (0, 255, 0), 2)
				box_dimensions=self.box[1]
				cv2.putText(img_box," Box Dim: "+str(round(box_dimensions[0],1))+","+str(round(box_dimensions[1],1))+" Angle: "+str(round(self.box[2],1)),(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.45, (0, 0, 255), 1)
				cv2.imshow('Computed',img_box)
		elif show_raw==False:
			cv2.destroyWindow('Threshold')
			cv2.destroyWindow('Grayscale')
		elif show_computed==False:
			cv2.destroyWindow('Computed')
			cv2.destroyWindow('Result')
	
	def compute_cropped_image(self, x1, x2):
		#self.dimXcropped=image.shape
		self.imageCropped=self.image[:,int(x1):int(x2)]
		#cv2.imshow('TestCropped',self.imageCropped)
	
	def checkIfNext(self,width,debug) :
		self.sliceWidth=int(width*self.dimY)
		if self.dimX>0:
			currentSlice=self.image[0:, 0:self.sliceWidth]
			#currentSlice=self.image[0:, (self.dimY-self.sliceWidth):]
			sumCurrentSlice=np.sum(currentSlice)
			if debug==True: print("sliceWidth: ",self.sliceWidth)
			if debug==True: print("SumSliceIn: ",sumCurrentSlice)
			if sumCurrentSlice < self.object_threshold : #to test
				if debug==True: print("True! delta: ",sumCurrentSlice - self.object_threshold)
				return True
			else:
				if debug==True: print("False! delta: ",sumCurrentSlice - self.object_threshold)
				return False
		else:
			return False
			
	def sumVerticalSlice(self,start,width,debug):
		if self.dimX>0:
			startPoint=int(self.dimY*start)
			sliceWidth=int(self.dimY*width)
			endPoint=startPoint+sliceWidth
			if debug==True: print("verticalSlice width: "+str(sliceWidth)+" start: "+str(startPoint)+" end: "+str(endPoint))
			currentSlice=self.image[0:, startPoint:endPoint]
			Area=np.sum(currentSlice)
			return Area 
		else:
			return 0
			
	def sumHorizontalSlice(self,start,width,debug):
		if self.dimX>0:
			startPoint=int(self.dimX*start)
			sliceWidth=int(self.dimX*width)
			endPoint=startPoint+sliceWidth
			if debug==True: print("verticalSlice width: "+str(sliceWidth)+" start: "+str(startPoint)+" end: "+str(endPoint))
			currentSlice=self.image[startPoint:endPoint,0:]
			Area=np.sum(currentSlice)
			return Area 
		else:
			return 0
	
			
	def checkDensity(self):
		self.totalArea=np.sum(self.image)
		return self.totalArea 
	
	def checkOutgoing(self, partOfImage,debug):
		if self.dimX>0:
			#partOfImage=0.6
			threshold=self.object_threshold*self.dimY*partOfImage/self.sliceWidth
			#currentSlice=self.image[0:, 0:int(self.dimY*partOfImage)]
			currentSlice=self.image[0:, (self.dimY-self.sliceWidth)*partOfImage:]
			threshold=self.object_threshold
			sumCurrentSlice=np.sum(currentSlice)
			if debug==True: print("SumSliceOut: ",sumCurrentSlice)
			if debug==True: print("threshold: ",threshold)
			if sumCurrentSlice > threshold : #to test
				if debug==True: print("True! delta: ",sumCurrentSlice - self.object_threshold)
				return True
			else:
				if debug==True: print("False! delta: ",sumCurrentSlice - self.object_threshold)
				return False
		else:
			return True
		
	def save_raw_image(self,saveSetting,objectNo, imageNo):
		if self.dimX>0:
			#now=format(time.time(),'.2f')
			now=datetime.datetime.now().strftime("%d_%m_%H_%M_%S_%f")
			if self.OrientationStatus=="BAD" and (saveSetting=="All Raw" or saveSetting=="All Parts") : 
				filename=self.controlImagePath+"bad_orient/time_"+str(now)+"_obj_"+str(objectNo).zfill(self.leadZeros)+"_bad_orient_raw.png"
				cv2.imwrite(filename, self.grayImage)
			elif self.OrientationStatus=="GOOD"  and (saveSetting=="All Raw" or saveSetting=="All Parts" or saveSetting=="All Good"): 
				filename=self.controlImagePath+"good/time_"+str(now)+"_obj_"+str(objectNo).zfill(self.leadZeros)+"_good_raw.png"
				cv2.imwrite(filename, self.grayImage)
			elif self.OrientationStatus=="FLIP" and (saveSetting=="All Raw" or saveSetting=="All Parts" or saveSetting=="All Good" ): 
				filename=self.controlImagePath+"flip/time_"+str(now)+"_obj_"+str(objectNo).zfill(self.leadZeros)+"_flip_raw.png"
				cv2.imwrite(filename, self.grayImage)
			elif self.SizeStatus=="BAD" and (saveSetting=="All Raw" or saveSetting=="All Parts"): 
				filename=self.controlImagePath+"bad_size/time_"+str(now)+"_obj_"+str(objectNo).zfill(self.leadZeros)+"_bad_size_raw.png"
				cv2.imwrite(filename, self.grayImage)	
			elif saveSetting=="All Raw": 
				filename=self.controlImagePath+"out/time_"+str(now)+"_obj_"+str(objectNo).zfill(self.leadZeros)+"_out_raw.png"
				cv2.imwrite(filename, self.grayImage)
		
	def save_analysed_image(self,saveSetting,objectNo, imageNo,debug):
		if self.dimX>0 and len(self.box)>0:
			if debug==True:  print("Save object No: ",imageNo)
			now=datetime.datetime.now().strftime("%d_%m_%H_%M_%S_%f")
			if self.SizeStatus=="BAD" and (saveSetting=="All Raw" or saveSetting=="All Parts" or saveSetting=="Contours"): 
				filename=self.controlImagePath+"bad_size/time_"+str(now)+"_obj_"+str(objectNo).zfill(self.leadZeros)+"_bad_size.png"
				img_box=cv2.cvtColor(self.image_orig, cv2.COLOR_GRAY2BGR)
				box = cv2.cv.BoxPoints(self.box) 
				box = np.array(box, dtype="int")
				cv2.drawContours(img_box, [box], -1, (255, 0, 0), 2)
				cv2.drawContours(img_box, self.contour_to_show, -1, (0, 255, 0), 2)
				box_dimensions=(round(self.box[1][0],2),round(self.box[1][1],2))
				cv2.putText(img_box," Box Dimensions: "+str(box_dimensions)+" Max: "+str(self.BoxMax)+" Min: "+str(self.BoxMin)+" Time: "+str(time.time()),(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.45, (0, 0, 255), 1)
				cv2.imwrite(filename, img_box)
			elif self.OrientationStatus=="BAD" and (saveSetting=="All Raw" or saveSetting=="All Parts" or saveSetting=="Contours"): 
				filename=self.controlImagePath+"bad_orient/time_"+str(now)+"_obj_"+str(objectNo).zfill(self.leadZeros)+"_bad_orient.png"
				cv2.imwrite(filename, self.analyzedImage)
			elif self.OrientationStatus=="FLIP" and (saveSetting=="All Raw" or saveSetting=="All Parts" or saveSetting=="All Good" or saveSetting=="Contours"): 
				filename=self.controlImagePath+"flip/time_"+str(now)+"_obj_"+str(objectNo).zfill(self.leadZeros)+"_flip.png"
				cv2.imwrite(filename, self.analyzedImage)
			elif self.OrientationStatus=="GOOD" and (saveSetting=="All Raw" or saveSetting=="All Parts" or saveSetting=="All Good" or saveSetting=="Contours"): 
				filename=self.controlImagePath+"good/time_"+str(now)+"_obj_"+str(objectNo).zfill(self.leadZeros)+"_good.png"
				cv2.imwrite(filename, self.analyzedImage)
			elif self.OrientationStatus=="UNKNOWN" and (saveSetting=="All Raw" or saveSetting=="All Parts" or saveSetting=="All Good" or saveSetting=="Contours"): 
				filename=self.controlImagePath+"unknown/time_"+str(now)+"_obj_"+str(objectNo).zfill(self.leadZeros)+"_unknown.png"
				cv2.imwrite(filename, self.image_orig)
	
	def set_recognition_parameters(self, BoxMax, BoxMin, EmptyBoxes,objectThreshold,imageThreshold,contourApprox, pixelTolerance ):
		self.BoxMax=BoxMax
		self.BoxMin=BoxMin
		self.EmptyBoxes=EmptyBoxes
		self.object_threshold=objectThreshold
		self.image_threshold=imageThreshold
		self.contourApprox=contourApprox
		self.contourApprox=contourApprox
		self.pixelTolerance = pixelTolerance 
		
	
	def check_box_dim(self):
		if self.get_selected_contour() == None or len(self.box)>0:
			self.SizeStatus="BAD"
			return False
		self.box = cv2.minAreaRect(self.contour_to_show)
		box_length=max(self.box[1])
		box_width=min(self.box[1])
		self.SizeStatus="BAD"
		checksum=0
		#check the max values
		if self.BoxMax[0]>0:
			if box_length<self.BoxMax[0]:
				checksum+=1
		else :
			checksum+=1
			
		if self.BoxMax[1]>0:
			if box_width<self.BoxMax[1]:
				checksum+=1
		else :
			checksum+=1
		#check the min values
		if self.BoxMin[0]>0:
			if box_length>self.BoxMin[0]:
				checksum+=1
		else :
			checksum+=1
			
		if self.BoxMin[1]>0:
			if box_width>self.BoxMin[1]:
				checksum+=1
		else :
			checksum+=1
		
		if checksum>=4 :
			#print("good box! Width: "+str(box_width)+" length: "+str(box_length))
			self.SizeStatus="GOOD"
			return True
		else :
			#print("bad box! Width: "+str(box_width)+" length: "+str(box_length))
			self.SizeStatus="BAD"
			return False
			
	def check_modular_boxes(self, angleLimit, debug):
		if len(self.contour_to_show) <= 0:
			self.OrientationStatus="BAD"
			return self.OrientationStatus
		BlockRectanglesGood=[]
		BlockRectanglesFlip=[]
		TestResultsGood=[]
		TestResultsFlip=[]
		boxTopRightX=0
		boxTopRightY=0
		boxBottomRightX=0
		boxBottomRightY=0
		boxBottomLeftX=0
		boxBottomLeftY=0
		boxTopLeftX=0
		boxTopLeftY=0
		img_box=cv2.cvtColor(self.image_orig, cv2.COLOR_GRAY2BGR)
		self.OrientationStatus="BAD"
		#self.box = cv2.minAreaRect(self.contour_to_show)
		box_angle=self.box[2]
		box_dimensions=self.box[1]
		box = cv2.cv.BoxPoints(self.box) 
		box = np.array(box, dtype="int")
		cv2.drawContours(img_box, [box], -1, ( 255,0,0), 2) #bgr
		cv2.drawContours(img_box, self.contour_to_show, -1, (0, 255,255), 2)
		if box_dimensions[0]<box_dimensions[1] :
			box_angle+=90
			
		if abs(box_angle)>angleLimit:
			#self.OrientationStatus="BAD"
			cv2.putText(img_box," Box Dim: "+str(round(box_dimensions[0],1))+","+str(round(box_dimensions[1],1))+" Time: "+str(time.time())+" Bad Angle: "+str(round(box_angle,2)),(10,10),cv2.FONT_HERSHEY_SIMPLEX,0.45, (0, 0, 255), 1)			
			self.analyzedImage=img_box
			return self.OrientationStatus
		#print("box angle: ",box_angle)
		#BlockRectanglesGood=np.zeros((1,4,2), dtype=np.int)	
		
		if box_angle<0:
			boxSorted=[box[box[:,1].argmin()],box[box[:,0].argmax()],box[box[:,1].argmax()],box[box[:,0].argmin()]]
			boxTopRightX=boxSorted[0][0]
			boxTopRightY=boxSorted[0][1]
			boxBottomRightX=boxSorted[1][0]
			boxBottomRightY=boxSorted[1][1]
			boxBottomLeftX=boxSorted[2][0]
			boxBottomLeftY=boxSorted[2][1]
			boxTopLeftX=boxSorted[3][0]
			boxTopLeftY=boxSorted[3][1]
		elif box_angle>0:
			boxSorted=[box[box[:,1].argmin()],box[box[:,0].argmax()],box[box[:,1].argmax()],box[box[:,0].argmin()]]
			boxTopLeftX=boxSorted[0][0]
			boxTopLeftY=boxSorted[0][1]
			boxTopRightX=boxSorted[1][0]
			boxTopRightY=boxSorted[1][1]
			boxBottomRightX=boxSorted[2][0]
			boxBottomRightY=boxSorted[2][1]
			boxBottomLeftX=boxSorted[3][0]
			boxBottomLeftY=boxSorted[3][1]
		else :
			maxX=box[box[:,0].argmax()][0]
			maxY=box[box[:,1].argmax()][1]
			
			#boxSorted=[box[box[:,1].argmin()],box[box[:,0].argmax()],box[box[:,1].argmax()],box[box[:,0].argmin()]]
			for i in range(0,4):
				if box[i][0]==maxX :
					if box[i][1]==maxY :
						boxBottomRightX=box[i][0]
						boxBottomRightY=box[i][1]
						if debug==True: print("bottomRx: "+str(boxBottomRightX)+" bottomRy: "+str(boxBottomRightY))
					else :
						boxTopRightX=box[i][0]
						boxTopRightY=box[i][1]
						if debug==True: print("TopRightx: "+str(boxTopRightX)+" TopRighty: "+str(boxTopRightY))
				else :
					if box[i][1]==maxY :
						boxBottomLeftX=box[i][0]
						boxBottomLeftY=box[i][1]
						if debug==True: print("bottomLx: "+str(boxBottomLeftX)+" bottomLy: "+str(boxBottomLeftY))
					else :
						boxTopLeftX=box[i][0]
						boxTopLeftY=box[i][1]
						if debug==True: print("TopLeftx: "+str(boxTopLeftX)+" TopLefty: "+str(boxTopLeftY))
		boxHeightX=boxBottomLeftX-boxTopLeftX
		boxHeightY=boxBottomLeftY-boxTopLeftY
		boxWidthX=boxBottomRightX-boxBottomLeftX
		boxWidthY=boxBottomRightY-boxBottomLeftY
		#print("pixelTolerance: ",self.pixelTolerance)
		#print("boxWidthX :"+str(boxWidthX)+" boxWidthY :"+str(boxWidthY)+" boxHeightX :"+str(boxHeightX)+" boxHeightY :"+str(boxHeightY)+" boxTopLeftX :"+str(boxTopLeftX)+" boxTopLeftY :"+str(boxTopLeftY))
		for i in range(0,len(self.EmptyBoxes)):
			#print("EmptyBoxes: ",self.EmptyBoxes[i])
			if self.EmptyBoxes[i][3]!=0:
				#print("we draw rectangle i: ",i)
				#print("EmptyBoxes in if: ",self.EmptyBoxes[i])
				#good boxes
				TopLeftX=boxTopLeftX+int(self.EmptyBoxes[i][0]*boxWidthX)+int(self.EmptyBoxes[i][1]*boxHeightX)
				TopLeftY=boxTopLeftY+int(self.EmptyBoxes[i][0]*boxWidthY)+int(self.EmptyBoxes[i][1]*boxHeightY)
				#print("WidthY :"+str(self.EmptyBoxes[i][1]*boxWidthY)+" HeightY: "+str(self.EmptyBoxes[i][1]*boxHeightY))
				TopRightX=TopLeftX+int(self.EmptyBoxes[i][2]*boxWidthX)
				TopRightY=TopLeftY+int(self.EmptyBoxes[i][2]*boxWidthY)
				BottomRightX=TopRightX+int(self.EmptyBoxes[i][2]*boxHeightX)
				BottomRightY=TopRightY+int(self.EmptyBoxes[i][2]*boxHeightY)
				BottomLeftX=BottomRightX-int(self.EmptyBoxes[i][2]*boxWidthX)
				BottomLeftY=BottomRightY-int(self.EmptyBoxes[i][2]*boxWidthY)
				whitePixel=[int(self.EmptyBoxes[i][3]),0]
				TopLeft=[TopLeftX,TopLeftY]
				TopRight=[TopRightX,TopRightY]
				BottomLeft=[BottomLeftX,BottomLeftY]
				BottomRight=[BottomRightX,BottomRightY]
				to_append=[TopLeft,TopRight,BottomRight,BottomLeft,whitePixel]
				to_append=np.array(to_append, dtype="int")
				BlockRectanglesGood.append(to_append)
				
				#flip boxes
				BottomRightX=boxBottomRightX-int(self.EmptyBoxes[i][0]*boxWidthX)-int(self.EmptyBoxes[i][1]*boxHeightX)
				BottomRightY=boxBottomRightY-int(self.EmptyBoxes[i][0]*boxWidthY)-int(self.EmptyBoxes[i][1]*boxHeightY)
				BottomLeftX=BottomRightX-int(self.EmptyBoxes[i][2]*boxWidthX)
				BottomLeftY=BottomRightY-int(self.EmptyBoxes[i][2]*boxWidthY)
				TopLeftX=BottomLeftX-int(self.EmptyBoxes[i][2]*boxHeightX)
				TopLeftY=BottomLeftY-int(self.EmptyBoxes[i][2]*boxHeightY)
				TopRightX=TopLeftX+int(self.EmptyBoxes[i][2]*boxWidthX)
				TopRightY=TopLeftY+int(self.EmptyBoxes[i][2]*boxWidthY)
				
				TopLeft=[TopLeftX,TopLeftY]
				TopRight=[TopRightX,TopRightY]
				BottomLeft=[BottomLeftX,BottomLeftY]
				BottomRight=[BottomRightX,BottomRightY]
				to_append=[TopLeft,TopRight,BottomRight,BottomLeft]
				to_append=np.array(to_append, dtype="int")
				BlockRectanglesFlip.append(to_append)
						
		for k in range(0, len(BlockRectanglesFlip)) :
				goodTest=0
				flipTest=0
				#general stuff that is identical for good and flip...
				Lx=BlockRectanglesGood[k][3][1]-BlockRectanglesGood[k][0][1]
				Ly=Lx
				whitePixel=BlockRectanglesGood[k][4][0]
				#print("whitePixel: ", whitePixel)
				#print("LxGood: ", Lx)
				pixelsToCheck=Lx*Ly
				checkTolerance=self.pixelTolerance*pixelsToCheck
				#good boxes
				#print("BlockRect: ",BlockRectanglesGood[k][3][1]-BlockRectanglesGood[k][0][1])
				P1xGood=BlockRectanglesGood[k][0][1]
				P1yGood=BlockRectanglesGood[k][0][0]
				P2xGood=P1xGood+Lx
				P2yGood=P1yGood+Ly
				rectangle_P1Good=(P1yGood,P1xGood)
				rectangle_P2Good=(P2yGood,P2xGood)
				rectGood=self.image_orig[P1xGood:P2xGood,P1yGood:P2yGood]
				sumOfrectGood=np.sum(rectGood)/255
				if whitePixel==1:
					acceptValue=pixelsToCheck-checkTolerance
					if sumOfrectGood>=acceptValue:
						goodTest=1
				elif whitePixel==-1:
					acceptValue=checkTolerance
					if sumOfrectGood<=acceptValue:
						goodTest=1
				if whitePixel==2 and k>0:
					acceptValue=pixelsToCheck-checkTolerance
					if sumOfrectGood>=acceptValue and TestResultsGood[k-1]==1:
						goodTest=1
				elif whitePixel==-2 and k>0:
					acceptValue=checkTolerance
					if sumOfrectGood<=acceptValue and TestResultsGood[k-1]==1:
						goodTest=1
				#if len(TestResultsGood)<k+1 :
				TestResultsGood.append(goodTest)
				#else:
				#	if TestResultsGood[k]<=0 :
				#		TestResultsGood[k]=goodTest
						
				if debug==True: print("sumofrect Good: "+str(sumOfrectGood)+" pixelsToCheck: "+str(pixelsToCheck)+" checkTolerance: "+str(checkTolerance) )
				#print("rectGood: ", rectGood)
				#print("rectangle_P1Good: ", rectangle_P1Good)
				#print("rectangle_P2Good: ", rectangle_P2Good)
				if goodTest==1:
					cv2.rectangle(img_box,rectangle_P1Good,rectangle_P2Good,( 255, 255, 0), 2) #bgr
				else: 
					cv2.rectangle(img_box,rectangle_P1Good,rectangle_P2Good,( 0, 0, 255), 2) #bgr
				#flip boxes
				P2xFlip=BlockRectanglesFlip[k][2][1]
				P2yFlip=BlockRectanglesFlip[k][2][0]
				P1xFlip=P2xFlip-Lx
				P1yFlip=P2yFlip-Ly
				rectangle_P1Flip=(P1yFlip,P1xFlip)
				rectangle_P2Flip=(P2yFlip,P2xFlip)
				rectFlip=self.image_orig[P1xFlip:P2xFlip,P1yFlip:P2yFlip]
				sumOfrectFlip=np.sum(rectFlip)/255
				if whitePixel==1:
					acceptValue=pixelsToCheck-checkTolerance
					if sumOfrectFlip>=acceptValue:
						flipTest=1
				elif whitePixel==-1:
					acceptValue=checkTolerance
					if sumOfrectFlip<=acceptValue:
						flipTest=1
				if whitePixel==2 and k>0:
					acceptValue=pixelsToCheck-checkTolerance
					if sumOfrectFlip>=acceptValue and TestResultsFlip[k-1]==1:
						flipTest=1
				elif whitePixel==-2 and k>0:
					acceptValue=checkTolerance
					if sumOfrectFlip<=acceptValue and TestResultsFlip[k-1]==1:
						flipTest=1
						
				#if len(TestResultsFlip)<k+1 :
				TestResultsFlip.append(flipTest)
				#else:
				#	if TestResultsFlip[k]<=0 :
				#		TestResultsFlip[k]=flipTest
				
				if debug==True: print("sumofrect Flip: ", sumOfrectFlip)
				#print("rectFlip: ", rectFlip)
				#print("rectangle_P1Flip: ", rectangle_P1Flip)
				#print("rectangle_P2Flip: ", rectangle_P2Flip)
				if flipTest==1:
					cv2.rectangle(img_box,rectangle_P1Flip,rectangle_P2Flip,( 0, 255, 0), 2) #bgr
				else:
					cv2.rectangle(img_box,rectangle_P1Flip,rectangle_P2Flip,( 0, 0, 255), 2)
		if sum(TestResultsGood)==len(TestResultsGood) and sum(TestResultsFlip)==0:
			self.OrientationStatus="GOOD"
		elif sum(TestResultsFlip)==len(TestResultsFlip) and sum(TestResultsGood)==0:
			self.OrientationStatus="FLIP"
		#else:
		#	self.OrientationStatus="BAD"	
		cv2.putText(img_box," Box Dim: "+str(round(box_dimensions[0],1))+","+str(round(box_dimensions[1],1))+" Time: "+str(time.time())+" Area: "+str(self.totalArea),(10,10),cv2.FONT_HERSHEY_SIMPLEX,0.45, (0, 0, 255), 1)
		cv2.putText(img_box," Box Angle: "+str(round(box_angle,1))+" testGood: "+str(TestResultsGood)+" testFlip: "+str(TestResultsFlip),(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.45, (0, 0, 255), 1)
		cv2.putText(img_box,"ORIENTATION: "+self.OrientationStatus+" SIZE: "+self.SizeStatus,(10,self.dimX-30),cv2.FONT_HERSHEY_SIMPLEX,1, (0, 0, 255), 1)
		#print("TestResultsFlip: ",TestResultsFlip)
		#if len(TestResultsGood)
		self.analyzedImage=img_box
		return self.OrientationStatus
	"""	
	def check_modular_boxes_old(self, angleLimit, debug):
		if len(self.contour_to_show) <= 0:
			self.OrientationStatus="BAD"
			return self.OrientationStatus
		BlockRectanglesGood=[]
		BlockRectanglesFlip=[]
		TestResultsGood=[]
		TestResultsFlip=[]
		img_box=cv2.cvtColor(self.image_orig, cv2.COLOR_GRAY2BGR)
		self.OrientationStatus="BAD"
		#self.box = cv2.minAreaRect(self.contour_to_show)
		box_angle=self.box[2]
		box_dimensions=self.box[1]
		box = cv2.cv.BoxPoints(self.box) 
		box = np.array(box, dtype="int")
		cv2.drawContours(img_box, [box], -1, (255, 0, 0), 2)
		cv2.drawContours(img_box, self.contour_to_show, -1, (0, 255, 0), 2)
		if box_dimensions[0]<box_dimensions[1] :
			box_angle+=90
			
		if abs(box_angle)>angleLimit:
			self.OrientationStatus="BAD"
			cv2.putText(img_box," Box Dim: "+str(round(box_dimensions[0],1))+","+str(round(box_dimensions[1],1))+" Time: "+str(time.time())+" Angle: "+str(round(box_angle,2)),(10,10),cv2.FONT_HERSHEY_SIMPLEX,0.45, (0, 0, 255), 1)			
			self.analyzedImage=img_box
			return self.OrientationStatus
		#print("box angle: ",box_angle)
		#BlockRectanglesGood=np.zeros((1,4,2), dtype=np.int)	
		
		if box_angle<0:
			boxSorted=[box[box[:,1].argmin()],box[box[:,0].argmax()],box[box[:,1].argmax()],box[box[:,0].argmin()]]
			boxTopRightX=boxSorted[0][0]
			boxTopRightY=boxSorted[0][1]
			boxBottomRightX=boxSorted[1][0]
			boxBottomRightY=boxSorted[1][1]
			boxBottomLeftX=boxSorted[2][0]
			boxBottomLeftY=boxSorted[2][1]
			boxTopLeftX=boxSorted[3][0]
			boxTopLeftY=boxSorted[3][1]
		elif box_angle>0:
			boxSorted=[box[box[:,1].argmin()],box[box[:,0].argmax()],box[box[:,1].argmax()],box[box[:,0].argmin()]]
			boxTopLeftX=boxSorted[0][0]
			boxTopLeftY=boxSorted[0][1]
			boxTopRightX=boxSorted[1][0]
			boxTopRightY=boxSorted[1][1]
			boxBottomRightX=boxSorted[2][0]
			boxBottomRightY=boxSorted[2][1]
			boxBottomLeftX=boxSorted[3][0]
			boxBottomLeftY=boxSorted[3][1]
		else :
			maxX=box[box[:,0].argmax()][0]
			maxY=box[box[:,1].argmax()][1]
			
			#boxSorted=[box[box[:,1].argmin()],box[box[:,0].argmax()],box[box[:,1].argmax()],box[box[:,0].argmin()]]
			for i in range(0,4):
				if box[i][0]==maxX :
					if box[i][1]==maxY :
						boxBottomRightX=box[i][0]
						boxBottomRightY=box[i][1]
						if debug==True: print("bottomRx: "+str(boxBottomRightX)+" bottomRy: "+str(boxBottomRightY))
					else :
						boxTopRightX=box[i][0]
						boxTopRightY=box[i][1]
						if debug==True: print("TopRightx: "+str(boxTopRightX)+" TopRighty: "+str(boxTopRightY))
				else :
					if box[i][1]==maxY :
						boxBottomLeftX=box[i][0]
						boxBottomLeftY=box[i][1]
						if debug==True: print("bottomLx: "+str(boxBottomLeftX)+" bottomLy: "+str(boxBottomLeftY))
					else :
						boxTopLeftX=box[i][0]
						boxTopLeftY=box[i][1]
						if debug==True: print("TopLeftx: "+str(boxTopLeftX)+" TopLefty: "+str(boxTopLeftY))
		boxHeightX=boxBottomLeftX-boxTopLeftX
		boxHeightY=boxBottomLeftY-boxTopLeftY
		boxWidthX=boxBottomRightX-boxBottomLeftX
		boxWidthY=boxBottomRightY-boxBottomLeftY
		#print("box: ",box)
		#print("boxWidthX :"+str(boxWidthX)+" boxWidthY :"+str(boxWidthY)+" boxHeightX :"+str(boxHeightX)+" boxHeightY :"+str(boxHeightY)+" boxTopLeftX :"+str(boxTopLeftX)+" boxTopLeftY :"+str(boxTopLeftY))
		for i in range(0,10):
			#print("EmptyBoxes: ",self.EmptyBoxes[i])
			if sum(self.EmptyBoxes[i])>0:
				#print("we draw rectangle i: ",i)
				#print("EmptyBoxes in if: ",self.EmptyBoxes[i])
				#print("BlockRect: ",BlockRectanglesGood)
				TopLeftX=boxTopLeftX+int(self.EmptyBoxes[i][0]*boxWidthX)+int(self.EmptyBoxes[i][1]*boxHeightX)
				TopLeftY=boxTopLeftY+int(self.EmptyBoxes[i][0]*boxWidthY)+int(self.EmptyBoxes[i][1]*boxHeightY)
				#print("WidthY :"+str(self.EmptyBoxes[i][1]*boxWidthY)+" HeightY: "+str(self.EmptyBoxes[i][1]*boxHeightY))
				TopRightX=TopLeftX+int(self.EmptyBoxes[i][2]*boxWidthX)
				TopRightY=TopLeftY+int(self.EmptyBoxes[i][2]*boxWidthY)
				BottomRightX=TopRightX+int(self.EmptyBoxes[i][3]*boxHeightX)
				BottomRightY=TopRightY+int(self.EmptyBoxes[i][3]*boxHeightY)
				BottomLeftX=BottomRightX-int(self.EmptyBoxes[i][2]*boxWidthX)
				BottomLeftY=BottomRightY-int(self.EmptyBoxes[i][2]*boxWidthY)
				
				TopLeft=[TopLeftX,TopLeftY]
				TopRight=[TopRightX,TopRightY]
				BottomLeft=[BottomLeftX,BottomLeftY]
				BottomRight=[BottomRightX,BottomRightY]
				to_append=[TopLeft,TopRight,BottomRight,BottomLeft]
				to_append=np.array(to_append, dtype="int")
				BlockRectanglesGood.append(to_append)
				
				BottomRightX=boxBottomRightX-int(self.EmptyBoxes[i][0]*boxWidthX)-int(self.EmptyBoxes[i][1]*boxHeightX)
				BottomRightY=boxBottomRightY-int(self.EmptyBoxes[i][0]*boxWidthY)-int(self.EmptyBoxes[i][1]*boxHeightY)
				BottomLeftX=BottomRightX-int(self.EmptyBoxes[i][2]*boxWidthX)
				BottomLeftY=BottomRightY-int(self.EmptyBoxes[i][2]*boxWidthY)
				TopLeftX=BottomLeftX-int(self.EmptyBoxes[i][3]*boxHeightX)
				TopLeftY=BottomLeftY-int(self.EmptyBoxes[i][3]*boxHeightY)
				TopRightX=TopLeftX+int(self.EmptyBoxes[i][2]*boxWidthX)
				TopRightY=TopLeftY+int(self.EmptyBoxes[i][2]*boxWidthY)
				
				TopLeft=[TopLeftX,TopLeftY]
				TopRight=[TopRightX,TopRightY]
				BottomLeft=[BottomLeftX,BottomLeftY]
				BottomRight=[BottomRightX,BottomRightY]
				to_append=[TopLeft,TopRight,BottomRight,BottomLeft]
				to_append=np.array(to_append, dtype="int")
				BlockRectanglesFlip.append(to_append)
		#BlockRectanglesGood = np.array(BlockRectanglesGood, dtype="int")
		#print("we draw rectangle points: ",len(BlockRectanglesFlip))
		for i in range(0, len(self.contour_to_show)):
			contourPoint=(self.contour_to_show[i][0][0],self.contour_to_show[i][0][1])
			for k in range(0, len(BlockRectanglesFlip)) :
				#cv2.drawContours(img_box, [BlockRectanglesGood[k]], -1, (255, 255, 0), 2) #light blue
				#cv2.drawContours(img_box, [BlockRectanglesFlip[k]], -1, (0, 255, 255), 2) #yellow
				goodTest=cv2.pointPolygonTest(BlockRectanglesGood[k],contourPoint,False)
				flipTest=cv2.pointPolygonTest(BlockRectanglesFlip[k],contourPoint,False)
				if len(TestResultsGood)<k+1 :
					TestResultsGood.append(goodTest)
				else:
					if TestResultsGood[k]<=0 :
						TestResultsGood[k]=goodTest
						
				if len(TestResultsFlip)<k+1 :
					TestResultsFlip.append(flipTest)
				else:
					if TestResultsFlip[k]<=0 :
						TestResultsFlip[k]=flipTest
		for k in range(0, len(BlockRectanglesFlip)) :
				cv2.drawContours(img_box, [BlockRectanglesGood[k]], -1, (255, 255, 0), 2) #light blue
				cv2.drawContours(img_box, [BlockRectanglesFlip[k]], -1, (0, 255, 255), 2) #yellow
		#print("TestResultsGood: ",max(TestResultsGood))
		if max(TestResultsGood)<0 and max(TestResultsFlip)>0:
			self.OrientationStatus="GOOD"
		elif max(TestResultsGood)>0 and max(TestResultsFlip)<0:
			self.OrientationStatus="FLIP"
		else:
			self.OrientationStatus="BAD"	
		cv2.putText(img_box," Box Dim: "+str(round(box_dimensions[0],1))+","+str(round(box_dimensions[1],1))+" Time: "+str(time.time())+" Area: "+str(self.totalArea),(10,10),cv2.FONT_HERSHEY_SIMPLEX,0.45, (0, 0, 255), 1)
		cv2.putText(img_box," Box Angle: "+str(round(box_angle,1))+" testGood: "+str(TestResultsGood)+" testFlip: "+str(TestResultsFlip),(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.45, (0, 0, 255), 1)
		cv2.putText(img_box,"ORIENTATION: "+self.OrientationStatus+" SIZE: "+self.SizeStatus,(10,self.dimX-30),cv2.FONT_HERSHEY_SIMPLEX,1, (0, 0, 255), 1)
		#print("TestResultsFlip: ",TestResultsFlip)
		#if len(TestResultsGood)
		self.analyzedImage=img_box
		return self.OrientationStatus
	"""