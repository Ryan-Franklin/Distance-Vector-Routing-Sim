import re
class helpers:

	def __init__(self):
		pass

	@classmethod
	def regexSplice (cls, str):
		return re.findall( r"[+-]?\d*\.d+|\d+", str)

	@classmethod
	def readFile (cls, fileName ) :
		topology = [ ]
		try :
			with open ( fileName , 'r' ) as inputFile :
				for line in inputFile :
					data = re.findall( r"[+-]?\d*\.d+|\d+", line)
					topology.append ( { "node1" : data [ 0 ] , "node2" : data [ 1 ] , "cost" : data [ 2 ] } )
					if not line :
						break
		except Exception as error :
			print ( "Error reading file." )
			print ( error )
		return topology

