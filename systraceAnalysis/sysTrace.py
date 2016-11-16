from ftrace import Ftrace
from ftrace import Interval
from FrameUnit import *
from numpy import average
from Alerts import*
class sysTrace:
    def __init__(self,filename):
        self.trace=Ftrace(filename)
       # print self.trace.android.framerate()
       # print self.trace.android.event_intervals()
        self.package="bbc.mobile.news.ww"
        VSYNC = float(1 / 60.)  # 16.67ms
        self.UI_THREAD_DRAW_NAMES = ['performTraversals', 'Choreographer#doFrame']
        self.RENDER_THREAD_DRAW_NAMES = ['DrawFrame']
        RENDER_THREAD_INDEP_DRAW_NAMES=["doFrame"]
        THREAD_SYNC_NAMES=["syncFrameState"]
        framenames = ['animator:'] + self.UI_THREAD_DRAW_NAMES + self.RENDER_THREAD_DRAW_NAMES
        self.frame_events=self.trace.android.frame_intervals()
        self.events=self.trace.android.event_intervals()


        print  "frame_event",len(self.trace.android.frame_intervals())
        print "render_event", len(self.trace.android.render_frame_intervals())
        print "ui_event",len(self.trace.android.ui_frame_intervals())
        render_intervals=self.trace.android.rendering_intervals()
        jank_intervals=self.trace.android.jank_intervals()

        app_latencies=self.trace.android.app_launch_latencies()
        event_names=self.trace.android.event_names
        #print app_latencies
        print event_names

        self.frameunits={}
        self.pid=0
        self.__GetAppPid()
        self.__Run()
        self.getFrameLength()

    def getFrameLength(self):
        durations=[]
        for id in self.frameunits:
            frameunit=self.frameunits[id]
            durations.append(frameunit.duration)
        print min(durations),max(durations),average(durations)



    def __GetAppPid(self):
        for frame in self.frame_events:
            if frame.event.task.name==self.package:
                self.pid=frame.pid
                break

    def GetAlerts(self):
        f=file("alertsInfo.csv",'w')
        for id in self.frameunits:
            frameunit=self.frameunits[id]
            alertCatch=Alerts(frameunit)
            realerts=alertCatch.Checking()
            for realert in realerts:
                writeline=self.package+","+str(id)+","+str(frameunit.start)+","+str(frameunit.end)+","+realert.alertTag+","+realert.alertinfo
                print writeline
                f.write(writeline+"\n")



    def GetJanks(self):
        f=file("janks.csv",'w')
        count=0
        for id in self.frameunits:
            frameunit=self.frameunits[id]
            if frameunit.duration>0.0167:
                count+=1
                writeline=self.package+","+str(id)+","+str(frameunit.start)+","+str(frameunit.end)+","+str(frameunit.duration)
                f.write(writeline+"\n")

        print "total janks:",count, "percentage:",count/float(len(self.frameunits))

        return
    def __Run(self):
        #for
        frames=self.frame_events
        eventnames=[]
        index=0
        id=0
        while index<len(self.frame_events):
            frame=self.frame_events[index]


            if frame.pid==self.pid and frame.name in self.UI_THREAD_DRAW_NAMES:
                renderindexs=self.__getRenderEvent(frame.interval.start,frame.interval.end,index+1)
                starttimes=[frame.interval.start]
                endtimes=[frame.interval.end]


                renderevents=[]
                allevents=[frame]
                #print frame

                frameunit=FrameUnit()
                frameunit.setId(id)
                frameunit.setUIFrame(frame)

                for renderindex in renderindexs:
                    renderevent=self.frame_events[renderindex]
                    allevents.append(renderevent)
                    renderevents.append(renderevent)
                    starttimes.append(renderevent.interval.start)
                    endtimes.append(renderevent.interval.end)
                    #print renderevent

                frameunit.setRenderFrame(renderevents)
                #print "start", min(starttimes)
                #print "end",max(endtimes)
                frameunit.setStart(min(starttimes))
                frameunit.setEnd(max(endtimes))
                frameunit.setDuration(max(endtimes)-min(starttimes))
                associateevents=self.__FindAssociateEvents(min(starttimes),max(endtimes))
                if len(associateevents)>0:
                    frameunit.AddEvents(associateevents)
                frameunit.AddEvent(frame)
                if len(renderevents)>0:
                    frameunit.AddEvents(renderevents)
                self.frameunits[id]=frameunit


                id+=1


                #break




            index+=1


    def __FindAssociateEvents(self,starttime,endtime):
        events=[]
        for event in self.events:
            if event.interval.start>=starttime and event.interval.end<=endtime:
                events.append(event)
        return events

    def __getRenderEvent(self,start,end,index):
        reindexs=[]
        while index<len(self.frame_events):
            cframe=self.frame_events[index]
            if cframe.interval.start>start and cframe.interval.start<end and cframe.event.task.name=="RenderThread" :
                reindexs.append(index)
            if cframe.interval.start>end:
                break
            index+=1
        return reindexs













