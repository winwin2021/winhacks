import sqlite3 as sql
import os
import sys

"""
Facility:
    Name: Name
    Location: City, Province/State, Country
    Equipment:
        Name: Name
            People_Trained: Number of people trained for the instrument
            Researchers: Number of researchers using them
            Publications: Number of publications the instrument is used in
            Students: Number of students learning with the instrument
            Samples: Number of samples processed by the instrument
            """

DB_PATH = 'dbs/' # default database path
STRING = 1
INT = 2
ANY = 3

def mprint(string): # custom print function
    print(f'> {string}')
    

def minput(string, type = 1): # custom input function
    '''
    type = 1 : string
    type = 2 : int
    type = 3 : any
    '''
    if type == 1:
        return str(input(f'> {string} '))
    if type == 2:
        return int(input(f'> {string} '))
    if type == 3:
        return input(f'> {string} ')


def __help(): # help command
    mprint('''COMMANDS:
    Help - Displays this message.
    Create [name] - Creates a database with the given name.
    Open [name] - Opens a database with the given name.
    InputFac - Prompt to input information about a certain facility into the open database.
    InputInstrument - Prompt to input information about a certain facility's equipment into the open database.
    Display - Display the data in the opened database.
    Close - Close the current database.
    Quit - Exit the program.
    ''')

def __create(manager, name = None): # create command
    if name is None:
        mprint('No database name given')
        return
    if manager is not None:
        manager.close_connection() # close previous manager
    manager = DatabaseManager(DB_PATH, name) # create DatabaseManager object for the given name and path
    manager.create_database() # create a new database
    return manager

def __open(manager, name = None): # open command
    if name is None:
        mprint('No database name given')
        return
    if manager is not None:
        manager.close_connection() # close previous manager
    manager = DatabaseManager(DB_PATH, name) 
    manager.open_database() # open the database
    return manager

def __inputfac(manager): # input facility command
    fac_name = minput('Facility Name:', STRING)
    city = minput('City:', STRING)
    province = minput('Province/State:', STRING)
    country = minput('Country:', STRING)

    equipmentinfo = []

    while True:
        if minput('Continue entering equipment? (1 for yes/0 for no)', INT) == 0:
            break

        name = minput('Equipment Name:', ANY)
        trained = minput('Number of People Trained:', INT)
        researchers = minput('Number of Researchers:', INT)
        publications = minput('Number of Publications:', INT)
        students = minput('Number of Students:', INT)
        samples = minput('Number of Samples:', INT)

        temp = (fac_name, name, trained, researchers, publications, students, samples)
        equipmentinfo.append(temp)

    manager.addfac(fac_name, city, province, country)
    if len(equipmentinfo) > 0:
        manager.addinstrument(equipmentinfo)

def __inputinstrument(manager): # input instrument command
    fac_name = minput('Facility Name:', STRING)

    equipmentinfo = []

    while True:
        name = minput('Equipment Name:', ANY)
        trained = minput('Number of People Trained:', INT)
        researchers = minput('Number of Researchers:', INT)
        publications = minput('Number of Publications:', INT)
        students = minput('Number of Students:', INT)
        samples = minput('Number of Samples:', INT)

        temp = (fac_name, name, trained, researchers, publications, students, samples)
        equipmentinfo.append(temp)

        if minput('Continue entering equipment? (1 for yes/0 for no)', INT) == 0:
            break

    manager.addinstrument(equipmentinfo)

def __display(manager): # display command
    manager.showall()

def __close(manager): # close command
    try:
        manager.close_connection() # close given manager if not already closed.
        return None
    except:
        mprint('No database to close')

class DatabaseManager:
    '''Database Manager class'''

    def __init__(self, path, name):
        self.path = path # path of database
        self.name = name # name of database
        self.build_name()
        self.dir = self.path + self.name # new directory
        self.conn = None # connection

    def grab(self, term):
        try:
            output = []
            c = self.conn.cursor()
            c.execute('SELECT rowid, * FROM instruments')
            instruments = c.fetchall()
            for instrument in instruments:
                if instrument[1] == term or instrument[2] == term:
                    c.execute(f'SELECT city FROM facilities WHERE fac_name = {instrument[1]}')
                    city = c.fetchone()
                    instrument.append(city)
                    output.append(instrument)
            return output
        except Exception as err:
            mprint(f'Failed to fetch data: {err}')

    def build_name(self):
        if not self.name.endswith('.db'):
            self.name += '.db'

    def get_name(self):
        return self.name

    def get_path(self):
        return self.path

    def get_dir(self):
        return self.dir

    def get_conn(self):
        return self.conn

    def showall(self):
        try:
            c = self.conn.cursor()
            c.execute('SELECT rowid, * FROM facilities')
            facilities = c.fetchall()
            mprint('{0:<5} {1:^15} {2:^15} {3:^15} {4:>15}'.format('Row', 'Facility Name', 'City', 'Province', 'Country'))
            mprint('-'*69)
            for facility in facilities:
                mprint('{0:<5} {1:^15} {2:^15} {3:^15} {4:>15}'.format(facility[0], facility[1], facility[2], facility[3], facility[4]))

            for i in range(3):
                mprint('')

            c.execute('SELECT rowid, * FROM instruments')
            instruments = c.fetchall()
            mprint('{0:<5} {1:^20} {2:^20} {3:^15} {4:^15} {5:^15} {6:^15} {7:>8}'.format('Row', 'Facility Name', 'Instrument Name', 'People Trained', 'Researchers', 'Publications', 'Students', 'Samples'))
            mprint('-'*120)
            for instrument in instruments:
                mprint('{0:<5} {1:^20} {2:^20} {3:^15} {4:^15} {5:^15} {6:^15} {7:>8}'.format(instrument[0], instrument[1], instrument[2], instrument[3], instrument[4], instrument[5], instrument[6], instrument[7]))
        except Exception:
            pass

        except Exception as err:
            mprint(f'Failed to fetch data from database: {err}')

    def addfac(self, fac_name, city, province, country):
        try:
            c = self.conn.cursor()
            mprint(f'Attempting to insert facility data into {self.name}')
            c.execute('SELECT rowid, * FROM facilities')
            facilities = c.fetchall()

            worked = 0
            
            for facility in facilities:
                if facility[1] == fac_name:
                    overwrite = minput('This facility is already in the database. Would you like to overwrite it? (1 for yes/0 for no)', INT)
                    if overwrite == 1:
                        c.execute(f'DELETE FROM facilities WHERE fac_name="{fac_name}"')
                        c.execute(f'INSERT INTO facilities VALUES ("{fac_name}", "{city}", "{province}", "{country}")')
                        worked = 1
                    else:
                        return
            
            if not worked:
                c.execute(f'INSERT INTO facilities VALUES ("{fac_name}", "{city}", "{province}", "{country}")')
            self.conn.commit()
            c.execute('VACUUM')
            mprint(f'Successfully added facility data into {self.name}')
        except Exception as err:
            mprint(f'Unable to add information to database: {err}')

    def addinstrument(self, instrumentinfos):
        try:
            c = self.conn.cursor()
            mprint(f'Attempting to insert instrument data into {self.name}')

            c.execute('SELECT rowid, * FROM instruments')
            instruments = c.fetchall()

            c.executemany(f'INSERT INTO instruments VALUES (?,?,?,?,?,?,?)', instrumentinfos)

            for instrument in instruments:
                for instrumentinfo in instrumentinfos:
                    if instrument[1] == instrumentinfo[0] and instrument[2] == instrumentinfo[1]:
                        overwrite = minput(f'This facilities instrument ({instrumentinfo[1]}) data is already in the database. Would you like to overwrite it? (1 for yes/0 for no)', INT)
                        if overwrite == 1:
                            c.execute(f'DELETE FROM instruments WHERE fac_name="{instrumentinfo[0]}" AND instrument_name="{instrumentinfo[1]}"')
                            c.executemany(f'INSERT INTO instruments VALUES (?,?,?,?,?,?,?)', [instrumentinfo])

            self.conn.commit()
            c.execute('VACUUM')
            mprint(f'Successfully added instrument data into {self.name}')
        except Exception as err:
            mprint(f'Unable to add information to database: {err}')

    def create_database(self):
        exists = os.path.exists(self.dir) # true/false if windows finds the path of the given database
        if exists:
            mprint(f'{self.name} already exists')
        else:
            mprint(f'Creating {self.name} ...')
            try:
                self.conn = sql.connect(self.dir) # try to create the database since it does not exist
                c = self.conn.cursor()
                c.execute("""CREATE TABLE facilities (
                                                    fac_name TEXT,
                                                    city TEXT,
                                                    province TEXT,
                                                    country TEXT
                                                    )""")
                                                    
                c.execute("""CREATE TABLE instruments (
                                                    fac_name TEXT,
                                                    instrument_name TEXT,
                                                    people_trained INT,
                                                    researchers INT,
                                                    publications INT,
                                                    students INT,
                                                    samples INT
                                                    )""")
                self.conn.commit()
                mprint(f'{self.name} created and opened successfully')
            except Exception as err: # creating the database failed
                mprint(f'Failed to create {self.name}: {err}')

    def open_database(self):
        exists = os.path.exists(self.dir) # true/false if windows finds the path of the given database
        if exists:
            mprint(f'{self.name} exists. Opening {self.name} ...')
            try:
                self.conn = sql.connect(self.dir) # try to open the database
                mprint(f'{self.name} opened successfully')
            except Exception as err: # opening the database failed
                mprint(f'Failed to open {self.name}: {err}')
        else:
            mprint(f'{self.name} does not exist')
    
    def check_exists(self):
        exists = os.path.exists(self.dir) # true/false if windows finds the path of the given database
        if exists:
            mprint(f'{self.name} exists')
        else:
            mprint(f'{self.name} does not exist')
        
    def close_connection(self):
        ''' Close connection to database '''

        if self.conn is not None:
            self.conn.close() # close database connection if it exists
            mprint(f'{self.name} closed successfully')
        else:
            mprint('No database to close')


def main():
    manager = None

    while True:
        cmd = minput('COMMAND', STRING)
        cmd = cmd.split(' ')
        kwrd = cmd[0].lower()
        if kwrd == 'help':
            __help()
        elif kwrd == 'create':
            try:
                manager = __create(manager, cmd[1])
            except IndexError:
                manager = __create(manager)
        elif kwrd == 'open':
            try:
                manager = __open(manager, cmd[1])
            except IndexError:
                manager = __open(manager)
        elif kwrd == 'inputfac':
            if manager is None:
                mprint('There is no database open')
            else:
                __inputfac(manager)
        elif kwrd == 'inputinstrument':
            if manager is None:
                mprint('There is no database open')
            else:
                __inputinstrument(manager)
        elif kwrd == 'display':
            __display(manager)
        elif kwrd == 'close':
            manager = __close(manager)
        elif kwrd == 'quit':
            sys.exit()
        else:
            mprint(f'{kwrd} is not a valid command')

if __name__ == '__main__':
    main()
