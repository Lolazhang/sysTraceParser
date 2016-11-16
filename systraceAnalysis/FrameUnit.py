class FrameUnit:
    def __init__(self):
        self.id=-1
        self.events=[]
        self.ui_thread=-1
        self.render_threads=[]
        self.start=-1 ## s
        self.end=-1 ##s
        self.duration=-1 ##s
    def setId(self,id):
        self.id=id
    def AddEvent(self,event):
        self.events.append(event)
    def AddEvents(self,events):
        self.events.extend(events)

    def setUIFrame(self,event):
        self.ui_thread=event
    def setRenderFrame(self,events):
        self.render_thread=events

    def setStart(self,start):
        self.start=start
    def setEnd(self,end):
        self.end=end
    def setDuration(self,duration):
        self.duration=duration