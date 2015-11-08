import adsk.core, adsk.fusion, traceback
import os, math

IDIOPHONE_NODE_RATIO = 0.225

handlers = []
app = adsk.core.Application.get()
ui = app.userInterface

def createNewComponent():
    root = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    return root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component

class ModalBarCommandExecuteHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        try:
            intputById = args.firingEvent.sender.commandInputs.itemById
            evaluate = app.activeProduct.unitsManager.evaluateExpression
            getInput = lambda id: evaluate(intputById(id).expression, "cm")

            l, w, h, b = getInput('barLength'), getInput('barWidth'), getInput('barHeight'), getInput('brightness')
            buildModalBar(l, w, h, b)

        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class ModalBarCommandDestroyHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        try:
            adsk.terminate()
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class ModalBarCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def notify(self, args):
        try:
            onExecute = ModalBarCommandExecuteHandler()
            args.command.execute.add(onExecute)
            handlers.append(onExecute)

            onDestroy = ModalBarCommandDestroyHandler()
            args.command.destroy.add(onDestroy)
            handlers.append(onDestroy)

            inputs = args.command.commandInputs
            val = adsk.core.ValueInput.createByReal

            inputs.addValueInput('barLength', 'Bar Length.', 'cm' , val (30.0))
            inputs.addValueInput('barWidth', 'Bar Width.', 'cm' , val (8.0))
            inputs.addValueInput('barHeight', 'Bar Height.', 'cm' , val(2.0))
            inputs.addValueInput('brightness', 'Brightness', '' , val(0.8))


        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def createExtrude(component, prof, thickness):
    join = adsk.fusion.FeatureOperations.JoinFeatureOperation
    extrudes = component.features.extrudeFeatures
    extInput = extrudes.createInput(prof, join)

    extInput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(thickness))
    return extrudes.add(extInput)

def buildModalBar(l, w, h, b):
    component = createNewComponent()
    if component is None:
        ui.messageBox('New component failed to create', 'New Component Failed')
        return

    sketch = component.sketches.add(component.xYConstructionPlane)

    sketchLine = sketch.sketchCurves.sketchLines.addByTwoPoints
    sketchCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius
    Point = adsk.core.Point3D.create

    #print sketch

    # Sketch the outline
    sketchLine(Point(0, 0, 0), Point(l, 0, 0))
    sketchLine(Point(l, 0, 0), Point(l, h, 0))
    sketchLine(Point(l, h, 0), Point(0, h, 0))
    sketchLine(Point(0, h, 0), Point(0, 0, 0))

    # Sketch the holes
    holeOffset = l * IDIOPHONE_NODE_RATIO
    sketchCircle(Point(holeOffset, h / 2, 0), 0.4)
    sketchCircle(Point(l - holeOffset, h / 2, 0), 0.4)

    # Sketch the arc
    points = adsk.core.ObjectCollection.create()

    points.add(Point(holeOffset, 0, 0))
    points.add(Point(l / 2,  h * b, 0))
    points.add(Point(l - holeOffset, 0, 0))

    sketch.sketchCurves.sketchFittedSplines.add(points)


    # Create the extrusion.
    extOne = createExtrude(component, sketch.profiles[3], w)

    extOne.faces[0].body.name = 'Modal Bar'

def run(context):
    try:
        commandId = 'ModalBar'
        cmdDef = ui.commandDefinitions.itemById(commandId)

        if not cmdDef:
            resourceDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources') # absolute resource file path is specified
            cmdDef = ui.commandDefinitions.addButtonDefinition(commandId, 'Create Modal Bar', 'Create Modal Bar', resourceDir)

        onCommandCreated = ModalBarCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        # keep the handler referenced beyond this function
        handlers.append(onCommandCreated)

        cmdDef.execute(adsk.core.NamedValues.create())

        adsk.autoTerminate(False)

    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
