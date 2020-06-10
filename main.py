################################################################################
##  				  SPARANZZA                                   ##
##  	         A imaginary world whitout hunger of freedmon                 ##
##  		           http://www.sparanzza.com                           ##
##  		            aurelio@sparanzza.com                             ##
##  	     This script create Ribbons from multiple curves seleted          ##
################################################################################

import maya.cmds as cmds

#Initialize global variables
nameCurveSelect = ""
widthIsoparm = 0
degreePathCurve = 0
spanCSPathCurve = 0
listIsoparm = []
sLocator = ""
eLocator = ""
wRib = 2
foAxisTF = 0
uAxisTF = 0
resRib = 1
sfTF = 0
efTF = 24
uniformCKB = True
thickness = True
meshRib= ""
groupRibContainer = ""

##CREATE RIBBON
def createRibbonEXE(*args):
	global nameCurveSelect
	global widthIsoparm
	global foAxisTF
	global uAxisTF
	global resRib
	global sfTF
	global efTF
	widthIsoparm = float(cmds.textField(ObjwRib, query = True, text = True))
	uniformCKB   = cmds.checkBox(ObjuniformCKB, query = True , value = True )
	thickness    = cmds.checkBox(Objthickness, query = True , value = True )
	foAxisTF     = str(cmds.textField(ObjfoAxisTF, query = True, text = True))
	uAxisTF      = str(cmds.textField(ObjuAxisTF, query = True, text = True))
	resRib       = int(cmds.textField(ObjresRib, query = True, text = True))
	sfTF         = int(cmds.textField(ObjsfTF, query = True, text = True))
	efTF         = int(cmds.textField(ObjefTF, query = True, text = True))

	
	listPath = cmds.ls(sl = True, dag = True)
	#At the end minus one in the range cause the last name in my Array is a DAG obj not the name
	# this list take nodeTransform and the Shape objects
	for indexList in range (0,len(listPath) - 1):
		if checkSelectionCurve(listPath[indexList + 1]):
			nameCurveSelect = listPath[indexList]
			infoCurve(nameCurveSelect)
			createIsoparm( widthIsoparm  , spanCSPathCurve  )
			pathAnimationMalaga(foAxisTF, uAxisTF, sfTF ,efTF ,nameCurveSelect ,listIsoparm )
			funcLoftIsoparm()
			layerPathRibbons()

##CHECK SELECTION DAG OBJECT
def checkSelectionCurve(curveFList):
	global nameCurveSelect
	##Check the type DAG object selected
	if cmds.objectType(curveFList, isType = "nurbsCurve"):
		## Get the name DAG curve selected
		return 1
	else:
		return 0
		
##NUMBER CV
def infoCurve(nameCurvePath):
	global degreePathCurve
	global spanCSPathCurve
	degreePathCurve = cmds.getAttr(nameCurvePath + '.degree')
	spanCSPathCurve = cmds.getAttr(nameCurvePath + '.spans')

##CREATE CURVE ISOPARM
def createIsoparm(width,cvSet):
	##Global Var mainPath
	global nameCurveSelect
	global listIsoparm 
	listIsoparm = []
	##index if not exist the first Group
	indexGRP = 1
	##check if exist and new Create empty Group
	while True:
		if not cmds.objExists(nameCurveSelect + '_TC_GRP_' + str(indexGRP)):
			cmds.group(em = True, name = nameCurveSelect + '_TC_GRP_' + str(indexGRP))
			break
		else:
			indexGRP += 1	
	# plus one because it is the last Isoparm to follow StartLocator
	numberIso = (cvSet * resRib )+ 1
	##Create Curve degree three
	for i in range (0, numberIso):
		curveAux = cmds.curve(name = nameCurveSelect + "Isop" + str(i),\
		 p=[(0, 0, 0), (float(width)/3.0, 0, 0),(float(width*2)/3.0, 0, 0),\
		 (width, 0, 0)])
		listIsoparm.append(curveAux)
		cmds.select(curveAux)
		cmds.CenterPivot()
		cmds.select(d = True)
		##Attach the curve in the Group 
		cmds.parent (curveAux,nameCurveSelect + '_TC_GRP_' + str(indexGRP))

##ATTACH THE CURVES TO PATH MOTION WITH OVERLAPING ANIMATION
def pathAnimationMalaga(foAxis, uAxis,sFrame,eFrame,pathCurve,ListIso):
	#variables
	global nameCurveSelect
	global spanCSPathCurve 
	global listIsoparm
	global sLocator
	global eLocator
	global resRib
	countAux = 0.0
	sCodeMP = ""
	eCodeMP = ""
	pathCodeMP  = ""
	SvalueLimit = 0.0
	EvalueLimit = 0.0

	##RebuildCurve to range 0 to 1
	cmds.rebuildCurve (pathCurve , kr = 0, kcp = True)
	#Create Locator to manipulate Ribbon
	sLocator = cmds.spaceLocator(name = "stRCtrl" + pathCurve ,p = (0,0,0))
	eLocator = cmds.spaceLocator(name = "eRCtrl" + pathCurve ,p = (0,0,0))
	#Attach Locators to Path Animation
	sCodeMP = cmds.pathAnimation (sLocator , pathCurve, name = 'moPath_' + sLocator[0] , fa = foAxis, \
 	ua = uAxis, su = 0, eu = 1, stu = sFrame, etu = eFrame )
	eCodeMP = cmds.pathAnimation (eLocator , pathCurve, name = 'moPath_' + eLocator[0] , fa = foAxis, \
 	ua = uAxis, su = 0, eu = 0)
	
	#Attach Isoparm to a individual motion Path and Expression Code
	for curList in ListIso:
		SvalueLimit =  str(countAux/float(spanCSPathCurve))
		EvalueLimit = str ((float(spanCSPathCurve) - countAux)/float(spanCSPathCurve))
		# Insert middle Isoparm take the value from Resolution, this value affect attribute Res Loft
		countAux += 1.0/resRib
		#Attach all isoparm curves and relations between the control
		pathCodeMP = cmds.pathAnimation (curList, pathCurve, name = 'MPath_' + str(curList) , fa = foAxis, \
 		ua = uAxis)
 		cmds.delete(pathCodeMP + '_uValue')
		#MEL Script insert for once Isoparm Curve
		codeForwardMotion = '$perCent = 0.001 * (' + sCodeMP + '.uValue / ' + str(countAux) + '); \n' \
		'if (' + sCodeMP + '.uValue >= ' + eCodeMP + '.uValue)\n' \
		+ '{\n' +  \
		'if ( ' + eCodeMP + '.uValue < ' +  SvalueLimit + ' )\n' \
		+ '{\n' +  \
			'if ( ' + sCodeMP + '.uValue >' + SvalueLimit + ' )\n' \
			+ '{\n' +  \
				pathCodeMP + '.uValue = ' + SvalueLimit + '- $perCent ;\n' \
			+ '}\r' +  \
			'if (' + sCodeMP + '.uValue <= ' + SvalueLimit + ' )\n' \
			+ '{\n' +  \
				pathCodeMP + '.uValue = ' +  sCodeMP + '.uValue - $perCent ; \n' \
			+ '}\n'  \
		+ '}\n' +  \
		'if (' + eCodeMP + '.uValue >=' + SvalueLimit + ' && ' + eCodeMP + '.uValue <= 1  )\n' \
		+ '{\n' +  \
			pathCodeMP + '.uValue = ' + eCodeMP + '.uValue; } \n} \n' 


		codeReverseMotion = 'if (' + sCodeMP + '.uValue < ' + eCodeMP + '.uValue)\n' \
		+ '{\n' +  \
		'if ( ' + eCodeMP + '.uValue >= ' +  SvalueLimit + ' )\n' \
		+ '{\n' +  \
			'if ( ' + sCodeMP + '.uValue <' + SvalueLimit + ' )\n' \
			+ '{\n' +  \
				pathCodeMP + '.uValue = ' + SvalueLimit +  ' + $perCent;\n' \
			+ '}\r' +  \
			'if (' + sCodeMP + '.uValue > ' + SvalueLimit + ' )\n' \
			+ '{\n' +  \
				pathCodeMP + '.uValue = ' +  sCodeMP + '.uValue  + $perCent; \n' \
			+ '}\n'  \
		+ '}\n' +  \
		'if (' + eCodeMP + '.uValue <' + SvalueLimit + ' && ' + eCodeMP + '.uValue > 0  )\n' \
		+ '{\n' +  \
			pathCodeMP + '.uValue = ' + eCodeMP + '.uValue; } \n} \n' \

		#Code String for All Expresion
		codeMel =  codeForwardMotion + codeReverseMotion 
		cmds.expression(o = str(curList) , n  = 'expr_' + str(curList) ,\
		s = codeMel , ae = True )

##FUNCTION TU CREATE SURFACE LOFT FROM LIST ISOPARM
def funcLoftIsoparm():
	global uniformCKB
	global meshRib
	SurfaceLoftRibbon = cmds.loft( listIsoparm, u = uniformCKB , ss = resRib, rn = 0, ch  = True, \
	name = nameCurveSelect +'Loft' )
	
	# if check the option extrude Ribbon
	if thickness :
		#cmds.editDisplayLayerMembers( 'SurfaceRibLayer', v )
		meshRib = cmds.nurbsToPoly(SurfaceLoftRibbon[0], format = 3, \
			name = 'Ribbon' + nameCurveSelect, ch = True )

##CREATE LAYERS TO DISTRIBUTE ALL CURVES AND SURFACE
def layerPathRibbons():
	global listIsoparm
	global nameCurveSelect
	global sLocator
	global eLocator
	global meshRib
	
	if not cmds.objExists('IsopRibLayer'):
		#Create Display Layers
		cmds.createDisplayLayer( noRecurse=True, name='IsopRibLayer' )
		cmds.createDisplayLayer( noRecurse=True, name='PathRibLayer' )
		cmds.createDisplayLayer( noRecurse=True, name='SurfaceRibLayer')
		cmds.createDisplayLayer( noRecurse=True, name='MeshRibLayer')
		cmds.createDisplayLayer( noRecurse=True, name='LocatorsRibLayer')
	cmds.editDisplayLayerMembers( 'IsopRibLayer', listIsoparm )
	cmds.editDisplayLayerMembers( 'PathRibLayer', nameCurveSelect )
	cmds.editDisplayLayerMembers( 'SurfaceRibLayer', nameCurveSelect +'Loft' )
	cmds.editDisplayLayerMembers( 'LocatorsRibLayer', sLocator )
	cmds.editDisplayLayerMembers( 'LocatorsRibLayer', eLocator )
	cmds.editDisplayLayerMembers( 'MeshRibLayer', meshRib[0] )

#########################WINDOWS PANEL TODOCINE#################################
winTC = cmds.window(title = "TCS" , widthHeight = (250,400) )
form = cmds.formLayout()
mainTabs = cmds.tabLayout(innerMarginWidth = 5, innerMarginHeight = 5)

cmds.formLayout (form, edit = True, attachForm = ((mainTabs , 'top', 0), \
(mainTabs , 'left', 0 ), (mainTabs ,'bottom', 0), (mainTabs ,'right', 0))) 

ribClay = cmds.rowColumnLayout( numberOfColumns=2, \
columnAttach=(1, 'right', 0), columnWidth=[(1, 100), (2, 100)])
cmds.text (label = 'Generate ribbon')
cmds.text (label = '  Sparanzza.com')
cmds.text (label = '')
cmds.text (label = '')
cmds.text (label = 'Width')
ObjwRib = cmds.textField(tx = '1') 

cmds.text (label = 'forward Axis')
ObjfoAxisTF = cmds.textField(tx = 'y')

cmds.text (label = 'Up Axis')
ObjuAxisTF = cmds.textField(tx = 'z')

cmds.text (label = 'Resolution (1 - 10)')
ObjresRib = cmds.textField(tx = '10')

cmds.text (label = 'Start Frame')
ObjsfTF = cmds.textField(tx = '0')

cmds.text (label = 'End Frame')
ObjefTF = cmds.textField(tx = '24')

cmds.text (label = '')
cmds.text (label = '')
cmds.text (label = '')
ObjuniformCKB = cmds.checkBox( label = 'Smooth')

cmds.text (label = '')
Objthickness = cmds.checkBox( label = 'thickness')

cmds.text (label = '')
cmds.text (label = '')
btnApl_rib = cmds.button(label = "Create Ribbon" , c = createRibbonEXE)
cmds.setParent("..")

animCLay = cmds.rowColumnLayout( numberOfColumns=2, \
columnAttach=(1, 'right', 0), columnWidth=[(1, 100), (2, 100)])
btnApl_anim = cmds.button(label = "Set Animation")
cmds.setParent("..")

scenCLay = cmds.rowColumnLayout( numberOfColumns=2, \
columnAttach=(1, 'right', 0), columnWidth=[(1, 100), (2, 100)])
btnScen_rib = cmds.button(label= "Create Scene")
cmds.setParent("..")

cmds.tabLayout (mainTabs , edit = True , tabLabel = ( (ribClay , "Ribbon"), \
(animCLay , "Animation"),(scenCLay , "Scene")))

cmds.showWindow(winTC)
##################################################################################







