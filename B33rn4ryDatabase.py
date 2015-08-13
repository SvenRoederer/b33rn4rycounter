class B33rn4ryDatabase():
  
  Database = None

  def __init__(self, dbtype='MYSQL'):
    if dbtype == 'MYSQL':
      self.Database = MysqlDatabase()
    elif dbtype == 'CONSOLE':
      self.Database = ConsoleDatabase()
    else:
      raise(NotImplementedError("unknown databse-type"))
    
  def checkUser(self, userID):
    return self.Database.checkUser(userID)
  
  def storeDraft(self, userID, pulses):
    self.Database.storeDraft(userID, pulses)
      
  def userConsumed(self):
    return -1

class ConsoleDatabase():

  validUsers = {
    '001',
    '3800C9C3B7',
#    '3800CA2422',
  }
  
  def checkUser(self, userID):
    if userID in self.validUsers:
      return ['user'+userID,]
    
  def userConsumed(self, userID):
    return -1
  
  def storeDraft(self, userID, pulses):
    print "user drafted %d pulses" % pulses

class MysqlDatabase():

  db = None
  cursor = None
  
  def __init__(self):
    import MySQLdb

    # Connect to mySQL db
    self.db = MySQLdb.connect(host="localhost", user="b33rn4ry", passwd="b33rn4ry", db="b33rn4rycounter")
    self.cursor=db.cursor()

  def checkUser(self, userID):
    self.cursor.execute ("SELECT `name` FROM `users` WHERE id = '"+userID+"';")
    return self.cursor.fetchone()

  def storeDraft(self, userID, pulses):
    self.cursor.execute ("Insert INTO 'consume' (userid, pulses) VALUES %s, %s" % (userID, pulses) )  
    print "user drafted %d pulses" % pulses
