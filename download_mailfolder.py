"""
Download all mails in a mailbox folder into the local file system and DELETE them in the mailbox.
"""

from imap_tools import MailBox, Q, AND  # (for search criteria)
import datetime
import json
import logging
import os   # for setting file timestamps
import sys  # to retrieve command line parameters
import traceback
import datetime


###############################################################################

LOG_TO_FILE = False

# logging.config.fileConfig('logging.conf')
logger = logging.getLogger('download_mailfolder')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)

if LOG_TO_FILE:
  # create file handler and set level to debug
  fileHandler = logging.FileHandler("download_mailfolder.log")
  fileHandler.setLevel(logging.DEBUG)

# create formatter (took out - %(name)s)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

# add formatter to consoleHandler
consoleHandler.setFormatter(formatter)
if LOG_TO_FILE:
  fileHandler.setFormatter(formatter)

# add consoleHandler to logger
logger.addHandler(consoleHandler)
if LOG_TO_FILE:
  logger.addHandler(fileHandler)

###############################################################################

def is_recipient(msg_to: list, mailaddress: str) -> bool:
  for recipient in msg_to:
    if recipient.startswith(mailaddress):
      return True
  return False

###############################################################################

def processMails(imapserver: str, username: str, password: str, imap_path: str,
                 directory_path: str, numberOfMessages: int, deleteAfterDownload: bool = False,
                 query: str = None) -> None:
  """
  imap_path should have a value like 'INBOX.2008', while
  directory_path is where the files (one for each message) get stored as *.eml file
  """
  # check if the output folder exists:
  # (right now, a terminal exception is being thrown if the folder doesn't exist)  
  # numberOfMessages = 5000
  count = 1
  totalcount = 0
  # query = AND(date_gte=datetime.date(2020, 1, 1), date_lt=datetime.date(2020, 2, 4))
  # get list of email messages from the specified folder
  with MailBox(imapserver).login(username, password, initial_folder=imap_path) as mailbox:
    logger.info("Mailbox {}@{}/{} opened ... ".format(username, imapserver, imap_path, sep=""))
    try:
      # Q(subject='Saludos'), 
      # for msg in mailbox.fetch(query, limit=numberOfMessages, miss_no_uid=True, miss_defect=False):  # Q(all=True)
      if query == None:
        query = Q(all=True)
      for msg in mailbox.fetch(query, limit=numberOfMessages, miss_no_uid=False, miss_defect=False, mark_seen=False):  # Q(all=True)
        totalcount += 1
        # sometimes there's an attribute error in the following line because the mail address cannot be parsed:
        name = msg.from_
        name = name.replace('/', '-')  # Deutsche Bahn puts LDAP info in their mail addresses ....
        # remove special characters from the subject line:
        subject = msg.subject.replace('/', '-').replace(' ', '_').replace('?', '_').replace('\x00', '').replace('\x09', '').replace('\x08', '').replace('\x0A', '').replace('\x0D', '')
        filename = "{}/{}_{}_({})_{}.eml".format(
          directory_path,
          datetime.datetime.strftime(msg.date, '%Y-%m-%d_%H-%M-%S'),
          name,
          msg.uid,
          subject[0:100]).replace('\x00', '').replace('\x09', '').replace('\x08', '').replace('\x0A', '').replace('\x0D', '')
        # logger.debug("{}/{}: Processing {} -> {}, {} ...".format(totalcount, numberOfMessages, name, msg.to, subject))
        if not os.path.isfile(filename):
          with open(filename, 'x', encoding='utf-8') as f:
            logger.info("{}/{}: Writing {} ...".format(count, numberOfMessages, filename))
            f.write(msg.obj.as_bytes().decode(encoding='ISO-8859-1'))
            if deleteAfterDownload:
              mailbox.delete(msg.uid)
              logger.debug("Deleted message uid {} ...".format(msg.uid))
            count += 1
          # set the time of the created file to the time of the e-mail:
          ts = msg.date.timestamp()
          os.utime(filename, (ts, ts))
        else:
          logger.warn("File {} already exists!".format(filename))
    except (RuntimeError, AttributeError) as error:
      logger.error("Error while processing message uid {}: {}".format(msg.uid, error))
      traceback.print_last()


def main(inputJsonFilename: str):
  # with open(inputJsonFilename, "w", encoding="utf8") as file:
  #   file.write(json.dumps(configurations, indent=2))
  with open(inputJsonFilename) as infile:
    logger.info("Loading mailbox configurations data from {0} ...".format(inputJsonFilename))
    configurations = json.load(infile)
  for config in configurations:
    if config['active']:
      if 'query' in config:
        query = config['query']
      else:
        query = None
      processMails(config['imapserver'], config['username'], config['password'],
                  config['imapfolder'], config['directory'],
                  config['numberOfMessages'], config['deleteAfterDownload'],
                  query)

###############################################################################

if __name__ == "__main__":
  main(sys.argv[1])
