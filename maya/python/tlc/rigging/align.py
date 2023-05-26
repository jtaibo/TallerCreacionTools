import maya.cmds as cmds

valueTranslation = []
valueRotation = []

copy = 'copy'
paste = 'paste'
copyPaste = 'copyPaste'

def message(value):
    windowMessage = cmds.window( widthHeight=(225, 20) , title = 'Align Tool')
    
    if value == 1:
        cmds.frameLayout('Select object')
        
    if value == 2:
        cmds.frameLayout('Dont select more of two objects')
        
    if value == 3:
        cmds.frameLayout('To use COPY-PASTE, select two objects')
    
    cmds.showWindow( windowMessage )

def checkAction(evento):
    valueCBtrans = cmds.checkBox('translation' , q = True , value = True)
    valueCBrot = cmds.checkBox('rotation' , q = True , value = True)
    valueCBrOrder = cmds.checkBox('rotationOrder' , q = True , value = True)
        
    selectObj = cmds.ls(selection = True)
    
    if selectObj != []:

        if len(selectObj) <= 2:
    
            if evento == 'copy':

                if valueCBtrans == True:
                    copyValueTrans(selectObj[0])
                    
                if valueCBrot == True:
                    copyValueRot(selectObj[0])
                
                if valueCBrOrder == True:
                    copyValueRorder(selectObj[0])
                
            if evento == 'paste':               
                pasteValue(selectObj[0])
                
            if evento == 'copyPaste':
                if len(selectObj) == 2:
                    if valueCBtrans == True:
                        copyValueTrans(selectObj[0])
                        
                    if valueCBrot == True:
                        copyValueRot(selectObj[0])
                        
                    if valueCBrOrder == True:
                        copyValueRorder(selectObj[0])
                        
                    pasteValue(selectObj[1])
                    
                else:
                    message(3)
        else:
            message(2)
            
    else:
         message(1)      
        

def copyValueTrans(obj):
    global valueTranslation
    valueTranslation = cmds.xform (obj , q = True , ws = True , t = True )     #recoje el valor global de posicón

    
def copyValueRot(obj):
    global valueRotation
    valueRotation = cmds.xform (obj , q = True , ws = True , ro = True )    #recoje el valor global de rotación

def copyValueRorder(obj):
    global roTarget
    roTarget = cmds.xform (obj , q = True ,rotateOrder= True )

def pasteValue(obj):
    obj_rotation=[0,0,0]    
    ro = cmds.xform (obj , q = True ,rotateOrder= True )
    valueCBtrans = cmds.checkBox('translation' , q = True , value = True)
    valueCBrot = cmds.checkBox('rotation' , q = True , value = True)
    valueCBrOrder = cmds.checkBox('rotationOrder' , q = True , value = True)

    if valueCBtrans == True:
        cmds.xform (obj , ws = True , t = valueTranslation )
        
    if valueCBrot == True:
            cmds.xform (obj , ws = True , ro = valueRotation, rotateOrder = roTarget)
            cmds.xform (obj , ws = True, rotateOrder = ro)
    
    if valueCBrOrder == True:
            cmds.xform (obj , ws = True , rotateOrder = roTarget)

def UIalign():

    if cmds.window ('UIalignObj' , exists = True):
        cmds.deleteUI ('UIalignObj') 
          
    cmds.window('UIalignObj' , widthHeight = (200, 50) , title = "Align Tool")
    
    cmds.columnLayout()
    cmds.separator( style = 'none' , height = 5 )
    cmds.rowLayout( numberOfColumns = 3 )
    
    CBtranslation = cmds.checkBox ('translation' , value = True , label = 'TRANSLATION')
    CBrotation = cmds.checkBox ('rotation' , value = True , label = 'ROTATION')
    CBrOrder = cmds.checkBox ('rotationOrder' , value = True , label = 'ROTATE ORDER')
    
    cmds.setParent( '..' )
    cmds.columnLayout()
    cmds.separator( style = 'none' , height = 5 ) 
    cmds.rowLayout( numberOfColumns = 5 )
    cmds.separator( style = 'single' , width = 10 )
    cmds.button( label = 'COPY', height = 18 , width = 50 , backgroundColor = [0, 100, 0] , command = 'checkAction(copy)')
    cmds.separator( style = 'single' , width = 25 )
    cmds.button( label = 'PASTE', height = 18 , width = 50 , backgroundColor = [0, 50, 50] , command = 'checkAction(paste)')
    
    cmds.setParent( '..' )
    cmds.columnLayout()
    cmds.separator( style = 'none' , height = 5 )
    cmds.rowLayout( numberOfColumns = 2 )
    cmds.separator( style = 'single' , width = 25 ) 
    cmds.button( label = 'COPY-PASTE', height = 18 , width = 100 , backgroundColor = [255, 30, 0] , command = 'checkAction(copyPaste)') 
    
    cmds.showWindow('UIalignObj') 
    
UIalign()