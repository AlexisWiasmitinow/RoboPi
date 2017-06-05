import cv2
#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg
import numpy as np
import time
from Quality_Measure import *

class ContourOperations:
	def __init__(self):
		self.image=[]
		self.box=[]
		self.contourlist=[]
		self.contoursorted=[]
		self.contour_to_show=[]
		self.area=0.0
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
		self.controlImagePath="control_images/"
		
	def set_lastScanTime(self,time) :
		self.lastScanTime=time
		
	def set_contour_no(self, contour_no):
		self.contour_no=contour_no
	
	def list_contours(self):
		if self.dimX>0:
			(cnts, _) = cv2.findContours(self.image, cv2.RETR_EXTERNAL, 2)
			#(cnts, _) = cv2.findContours(self.image, cv2.RETR_TREE, 1)
			#CHAIN_APPROX_SIMPLE CV_CHAIN_APPROX_TC89_L1,CV_CHAIN_APPROX_TC89_KCOS
			#cv::CHAIN_APPROX_NONE = 1,   cv::CHAIN_APPROX_SIMPLE = 2,  cv::CHAIN_APPROX_TC89_L1 = 3,  cv::CHAIN_APPROX_TC89_KCOS = 4
			
			cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
			self.contoursorted=cnts
		
	def get_selected_contour(self):
		self.list_contours()
		if len(self.contoursorted)>1:
			self.contour_to_show=self.contoursorted[self.contour_no]
			#del contour_to_show[0]
			#print("showcontour")
			return self.contour_to_show
		else: 
			print("no contour!")
			return None  
	
	def get_selected_area(self):
		self.area=cv2.contourArea(self.contour_to_show)
		return self.area
	
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
		#cv2.imshow('Test',self.image)
	
	def showPreview(self, show_raw, show_computed):
		if show_raw==True and show_computed==False and self.dimX>0:
			cv2.imshow('Threshold',self.image)
			cv2.imshow('Grayscale',self.grayImage)
		elif show_computed==True and len(self.box)>0:
			img_box=cv2.cvtColor(self.image, cv2.COLOR_GRAY2BGR)
			box = cv2.cv.BoxPoints(self.box) 
			box = np.array(box, dtype="int")
			cv2.drawContours(img_box, [box], -1, (255, 0, 0), 2)
			cv2.drawContours(img_box, self.contour_to_show, -1, (0, 255, 0), 2)
			box_dimensions=self.box[1]
			cv2.putText(img_box," Box Dimensions: "+str(box_dimensions)+" Time: "+str(time.time()),(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.45, (255, 255, 255), 2)
			cv2.imshow('Computed',img_box)
		elif show_raw==False:
			cv2.destroyWindow('Threshold')
			cv2.destroyWindow('Grayscale')
		elif show_computed==False:
			cv2.destroyWindow('Computed')
	
	def compute_cropped_image(self, x1, x2):
		#self.dimXcropped=image.shape
		self.imageCropped=self.image[:,int(x1):int(x2)]
		#cv2.imshow('TestCropped',self.imageCropped)
	
	def checkIfNext(self,lastTakeNext) :
		sliceWidth=10
		if self.dimX>0:
			currentSlice=self.image[0:self.dimX, (self.dimY-sliceWidth):self.dimY]
			sumCurrentSlice=np.sum(currentSlice)
			if sumCurrentSlice < self.object_threshold : #to test
				#print("True! delta: ",sumCurrentSlice - self.object_threshold)
				return True
			else:
				#print("False! delta: ",sumCurrentSlice - self.object_threshold)
				return False
		else:
			return False
			
	def save_raw_image(self,saveSetting,objectNo, imageNo):
		now=format(time.time(),'.2f')
		if self.OrientationStatus=="BAD" and (saveSetting=="All Raw" or saveSetting=="All Parts") : 
			filename=self.controlImagePath+"bad_orient/"+str(imageNo).zfill(self.leadZeros)+"_time_"+str(now)+"_obj_"+str(objectNo).zfill(self.leadZeros)+"_bad_orient_raw.png"
			cv2.imwrite(filename, self.grayImage)
		elif self.OrientationStatus=="GOOD"  and (saveSetting=="All Raw" or saveSetting=="All Parts" or saveSetting=="All Good" or saveSetting=="Contours"): 
			filename=self.controlImagePath+"good/"+str(imageNo).zfill(self.leadZeros)+"_time_"+str(now)+"_obj_"+str(objectNo).zfill(self.leadZeros)+"_good_raw.png"
			cv2.imwrite(filename, self.grayImage)
		elif self.OrientationStatus=="FLIP" and (saveSetting=="All Raw" or saveSetting=="All Parts" or saveSetting=="All Good" or saveSetting=="Contours"): 
			filename=self.controlImagePath+"flip/"+str(imageNo).zfill(self.leadZeros)+"_time_"+str(now)+"_obj_"+str(objectNo).zfill(self.leadZeros)+"_flip_raw.png"
			cv2.imwrite(filename, self.grayImage)
		elif self.SizeStatus=="BAD" and (saveSetting=="All Raw" or saveSetting=="All Parts"): 
			filename=self.controlImagePath+"bad_size/"+str(imageNo).zfill(self.leadZeros)+"_time_"+str(now)+"_obj_"+str(objectNo).zfill(self.leadZeros)+"_bad_size_raw.png"
			cv2.imwrite(filename, self.grayImage)	
		elif saveSetting=="All Raw": 
			filename=self.controlImagePath+"out/"+str(imageNo).zfill(self.leadZeros)+"_time_"+str(now)+"_obj_"+str(objectNo).zfill(self.leadZeros)+"_out_raw.png"
			cv2.imwrite(filename, self.grayImage)
		
	def save_analysed_image(self,saveSetting,objectNo, imageNo):
		now=format(time.time(),'.2f')
		if self.SizeStatus=="BAD" and (saveSetting=="All Raw" or saveSetting=="All Parts" or saveSetting=="Contours"): 
			filename=self.controlImagePath+"bad_size/"+str(imageNo).zfill(self.leadZeros)+"_time_"+str(now)+"_obj_"+str(objectNo).zfill(self.leadZeros)+"_bad_size.png"
			img_box=cv2.cvtColor(self.image, cv2.COLOR_GRAY2BGR)
			box = cv2.cv.BoxPoints(self.box) 
			box = np.array(box, dtype="int")
			cv2.drawContours(img_box, [box], -1, (255, 0, 0), 2)
			cv2.drawContours(img_box, self.contour_to_show, -1, (0, 255, 0), 2)
			box_dimensions=(round(self.box[1][0],2),round(self.box[1][1],2))
			cv2.putText(img_box," Box Dimensions: "+str(box_dimensions)+" Max: "+str(self.BoxMax)+" Min: "+str(self.BoxMin)+" Time: "+str(time.time()),(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.45, (255, 255, 255), 2)
			cv2.imwrite(filename, img_box)
		elif self.OrientationStatus=="BAD" and (saveSetting=="All Raw" or saveSetting=="All Parts"): 
			filename=self.controlImagePath+"bad_orient/"+str(imageNo).zfill(self.leadZeros)+"_time_"+str(now)+"_obj_"+str(objectNo).zfill(self.leadZeros)+"_bad_orient.png"
			cv2.imwrite(filename, self.analyzedImage)
		elif self.OrientationStatus=="FLIP" and (saveSetting=="All Raw" or saveSetting=="All Parts" or saveSetting=="All Good" or saveSetting=="Contours"): 
			filename=self.controlImagePath+"flip/"+str(imageNo).zfill(self.leadZeros)+"_time_"+str(now)+"_obj_"+str(objectNo).zfill(self.leadZeros)+"_flip.png"
			cv2.imwrite(filename, self.analyzedImage)
		elif self.OrientationStatus=="GOOD" and (saveSetting=="All Raw" or saveSetting=="All Parts" or saveSetting=="All Good" or saveSetting=="Contours"): 
			filename=self.controlImagePath+"good/"+str(imageNo).zfill(self.leadZeros)+"_time_"+str(now)+"_obj_"+str(objectNo).zfill(self.leadZeros)+"_good.png"
			cv2.imwrite(filename, self.analyzedImage)
		
		#filename=self.controlImagePath+"bad_size/"+str(imageNo).zfill(self.leadZeros)+"_time_"+str(now)+"_obj_"+str(objectNo).zfill(self.leadZeros)+"_scanned.png"
		#cv2.imwrite(filename, self.analyzedImage)
		#elif self.SizeStatus=="GOOD" :
		#self.savePicsOptions=( "All Raw", "All Good", "All Parts","Contours","None")
	
	def load_image(self):
		self.image=cv2.imread("sample_images/sample.png", 0)
		self.dimX , self.dimY = self.image.shape[:2]
	
	def set_resize_factor(self, factor):
		self.show_scale_factor=factor
		
	def image_resize(self, image):
		return cv2.resize(image,(int(self.dimY*self.show_scale_factor),int(self.dimX*self.show_scale_factor)),interpolation = cv2.INTER_AREA)
	
	def check_status(self):
		return self.OrientationStatus
	
	#def show_box(self, plot_title):
	#	cv2.imshow(plot_title,self.image_resize(self.check_modular_boxes()))
	
	def set_recognition_parameters(self, BoxMax, BoxMin, EmptyBoxes):
		self.BoxMax=BoxMax
		self.BoxMin=BoxMin
		self.EmptyBoxes=EmptyBoxes
		
	
	def check_box_dim(self):
		if self.get_selected_contour() == None:
			self.SizeStatus="BAD"
			return self.SizeStatus
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
			
	def check_modular_boxes(self):
		if len(self.contour_to_show) <= 0:
			self.OrientationStatus="BAD"
			return self.OrientationStatus
		BlockRectanglesGood=[]
		BlockRectanglesFlip=[]
		TestResultsGood=[]
		TestResultsFlip=[]
		img_box=cv2.cvtColor(self.image, cv2.COLOR_GRAY2BGR)
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
						#print("bottomRx: "+str(boxBottomRightX)+" bottomRy: "+str(boxBottomRightY))
					else :
						boxTopRightX=box[i][0]
						boxTopRightY=box[i][1]
						#print("TopRightx: "+str(boxTopRightX)+" TopRighty: "+str(boxTopRightY))
				else :
					if box[i][1]==maxY :
						boxBottomLeftX=box[i][0]
						boxBottomLeftY=box[i][1]
						#print("bottomLx: "+str(boxBottomLeftX)+" bottomLy: "+str(boxBottomLeftY))
					else :
						boxTopLeftX=box[i][0]
						boxTopLeftY=box[i][1]
						#print("TopLeftx: "+str(boxTopLeftX)+" TopLefty: "+str(boxTopLeftY))
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
		statusText=""
		for i in range(0, len(self.contour_to_show)):
			contourPoint=(self.contour_to_show[i][0][0],self.contour_to_show[i][0][1])
			for k in range(0, len(BlockRectanglesFlip)) :
				cv2.drawContours(img_box, [BlockRectanglesGood[k]], -1, (255, 255, 0), 2) #light blue
				cv2.drawContours(img_box, [BlockRectanglesFlip[k]], -1, (0, 255, 255), 2) #yellow
				if len(TestResultsGood)<k+1 :
					TestResultsGood.append(cv2.pointPolygonTest(BlockRectanglesGood[k],contourPoint,False))
				else:
					if TestResultsGood[k]<=0 :
						TestResultsGood[k]=cv2.pointPolygonTest(BlockRectanglesGood[k],contourPoint,False)
						
				if len(TestResultsFlip)<k+1 :
					TestResultsFlip.append(cv2.pointPolygonTest(BlockRectanglesFlip[k],contourPoint,False))
				else:
					if TestResultsFlip[k]<=0 :
						TestResultsFlip[k]=cv2.pointPolygonTest(BlockRectanglesFlip[k],contourPoint,False)
		#print("TestResultsGood: ",max(TestResultsGood))
		if max(TestResultsGood)<0 and max(TestResultsFlip)>0:
			self.OrientationStatus="GOOD"
		elif max(TestResultsGood)>0 and max(TestResultsFlip)<0:
			self.OrientationStatus="FLIP"
		else:
			self.OrientationStatus="BAD"	
		cv2.putText(img_box," Box Dimensions: "+str(box_dimensions)+" Time: "+str(time.time()),(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.45, (255, 255, 255), 2)
		#cv2.putText(img_box," Box Dimensions: "+str(box_dimensions)+" Time: "+str(time.time())+" Delta Time: "+str(QualityMeasures['deltaTime'])+" Delta Good: "+str(QualityMeasures['deltaGood']),(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.45, (255, 255, 255), 2)
		cv2.putText(img_box,"ORIENTATION: "+self.OrientationStatus+" SIZE: "+self.SizeStatus,(10,self.dimX-30),cv2.FONT_HERSHEY_SIMPLEX,1, (255, 255, 255), 2)
		#print("TestResultsFlip: ",TestResultsFlip)
		#if len(TestResultsGood)
		self.analyzedImage=img_box
		return self.OrientationStatus