import sys,tty,termios

# threads Library
import threading

import time

### Start Key reader Thread  classes ###

# Class that gets keys from keyboard. Taken from http://stackoverflow.com/questions/22397289/finding-the-values-of-the-arrow-keys-in-python-why-are-they-triples
class _Getch:
	def __call__(self):
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		try:
			tty.setraw(sys.stdin.fileno())
			ch = sys.stdin.read(3)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
		return ch

# Class that contains a _Getch object to detect if the keys pressed by the user are arrows (and which) or not
class _ArrowsReader:
	def __init__(self):
		pass

	def getKey(self):
		inkey = _Getch()
		retKey = "null"
		while(1):
			k=inkey()
			if k!='':break
		if k=='\x1b[A':
			retKey = "up"
		elif k=='\x1b[B':
			retKey = "down"
		elif k=='\x1b[C':
			retKey = "right"
		elif k=='\x1b[D':
			retKey = "left"
		elif k=='qqq':
			retKey = "quit"
		elif k=='\u001b\u001b\u001b':
			retKey = "quit"
		elif k=='qwe':
			retKey = "quit"
		else:
			retKey = "null"
		return retKey
			
class _ArrowsReaderThread(threading.Thread):
	def __init__(self,toNotify):
		threading.Thread.__init__(self)
		self.arrowReader = _ArrowsReader()
		self.toNotify = toNotify
		pass
	
	def run(self):
		quit = False
		while not(quit):
			key = self.arrowReader.getKey()
			if key == "quit":
				quit = True
			self.toNotify.notifyStr(key)
			
### End Key reader Thread classes ###

# Uses locks to protect concurrent access to buffers
class ActionsKeywordBuffers():
	def __init__(self):
		self.bufSpeed = [0, 0, 0, 1, 0, 0, 0]
		self.bufDirect = [0, 0, 0, 1, 0, 0, 0]
		self.bufSpeedLock = threading.RLock()
		self.bufDirectLock = threading.RLock()
		pass

	def restart(self):
		self.bufSpeed = [0, 0, 0, 1, 0, 0, 0]
		self.bufDirect = [0, 0, 0, 1, 0, 0, 0]

	def notifyStr(self,string):
		self._handleArrow(string)
		#self._printBuffers() # Uncomment to see the content of the buffers when received the update
		
	def _handleArrow(self,arrow):
		if arrow=="up":
			self.bufSpeedLock.acquire()
			self._switchBuffer(self.bufSpeed,True)
			self.bufSpeedLock.release()
		elif arrow=="down":
			self.bufSpeedLock.acquire()
			self._switchBuffer(self.bufSpeed,False)
			self.bufSpeedLock.release()
		elif arrow=="right":
			self.bufDirectLock.acquire()
			self._switchBuffer(self.bufDirect,False)
			self.bufDirectLock.release()
		elif arrow=="left":
			self.bufDirectLock.acquire()
			self._switchBuffer(self.bufDirect,True)
			self.bufDirectLock.release()
	
	# Be careful! Assure that buffer is locked by the calling function
	def _switchBuffer(self,buf,swToBigger):
		maxLen = len(buf)
		currentPos = -1
		for i in [i for i,x in enumerate(buf) if x == 1]:
			currentPos = i # Find where is the 1 number in the list
			break
		if swToBigger:
			if currentPos<maxLen-1:
				buf[currentPos]=0
				buf[currentPos+1]=1
		else:
			if currentPos>0:
				buf[currentPos]=0
				buf[currentPos-1]=1
			
	def _printBuffers(self):
		self.bufSpeedLock.acquire()
		print("Speed: ",self.bufSpeed)
		self.bufSpeedLock.release()
		self.bufDirectLock.acquire()
		print("Direction: ",self.bufDirect)
		self.bufDirectLock.release()
		
	def getBufSpeed(self):
		self.bufSpeedLock.acquire()
		bufSpeedCopy = list(self.bufSpeed)
		self.bufSpeedLock.release()
		return bufSpeedCopy
	
	def getBufDirect(self):
		self.bufDirectLock.acquire()
		bufDirectCopy = list(self.bufDirect)
		self.bufDirectLock.release()
		return bufDirectCopy


if __name__ == '__main__':
	arrowsListener = ActionsKeywordBuffers()
	arrowsListenerThread = _ArrowsReaderThread(arrowsListener)
	arrowsListenerThread.start()

	for i in range(10000):
		speed = arrowsListener.getBufSpeed()
		direction = arrowsListener.getBufDirect()
		print("--------------", "\r")
		print("From main", "\r")
		print("Speed: ",speed, "\r")
		print("Direction: ",direction, "\r")
		print("--------------", "\r")
		time.sleep(1)