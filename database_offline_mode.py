import sqlite3 as sql
import os
import json

FILE_PATH = "database_offline_mode.db"

def user_verification_status_convert(user_verification_status: bool) -> int:
    if user_verification_status:
        return 1
    return 0

class Database:

    def __init__(self):
        self.connect = sql.connect(FILE_PATH)
        self.cursor = self.connect.cursor()

    # =================================== tables creating ============================

    def create_user_table(self) -> None:

        """
        Creating a user table
        (user_id -> primary key, full_name, citizen_id, email, email_password, user_verification_status)
        attributes

        :return: None
        """

        execution_query = """ --sql 
            CREATE TABLE IF NOT EXISTS User_table (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT ,
                email TEXT UNIQUE NOT NULL, 
                password_hash TEXT NOT NULL,                
                full_name TEXT NOT NULL,
                nationality TEXT NOT NULL,
                language TEXT NOT NULL,
                phone TEXT,
                role TEXT NOT NULL,
                user_verification_status INTEGER NOT NULL CHECK ( user_verification_status IN (0, 1) ),
                avatar_url TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, -- CHECK FOR PERMISSION 
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """

        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self.cursor.execute(execution_query)
        self.connect.commit()

        print("User table has been created successfully..")

    def create_passport_table(self) -> None:

        """
        Theis method for creating a passport table with
        (passport_id -> primary key, full_name_passport, passport_expiration_date) as attributes and
        user_id as a foreign key from user_table.

        :return: None
        """

        execution_query = """--sql
        CREATE TABLE IF NOT EXISTS Passport_table (
            passport_id TEXT PRIMARY KEY,
            user_id INTEGER,
            full_name_passport TEXT,
            passport_expiration_date TEXT,
            FOREIGN KEY (user_id) REFERENCES User_table(user_id) ON DELETE CASCADE
        );
        """

        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self.cursor.execute(execution_query)
        self.connect.commit()

        print('Passport table has been create successfully...')

    def create_visa_table(self) -> None:
        """
        This method for creating a visa table with
        (reference_no -> primary key, visa_type, purpose_of_visit, arrival_date, departure_date, visa_application_status) and as attributes
        (user_id, passport_id) as foreign keys.

        :return: None
        """
        execution_query = """--sql
            CREATE TABLE IF NOT EXISTS Visa_table (
                reference_no TEXT PRIMARY KEY,
                user_id INTEGER,
                passport_id TEXT,
                visa_type TEXT,
                purpose_of_visit TEXT,
                arrival_date TEXT,
                departure_date TEXT,
                visa_application_status TEXT,
                FOREIGN KEY (user_id) REFERENCES User_table(user_id) ON DELETE CASCADE ,
                FOREIGN KEY (passport_id) REFERENCES Passport_table(passport_id)
            );
        """

        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self.cursor.execute(execution_query)
        self.connect.commit()

        print("Visa table has been created successfully.. ")

    def create_jordan_pass_table(self) -> None:
        """
        This method for creating a jordan pass table with
        (pass_id -> primary key, jordan_pass_expiration_date, jordan_pass_active_status) as attributes and
        (user_id, visa_references_no) as foreign keys.
        :return: None
        """
        execution_query = """--sql
            CREATE TABLE IF NOT EXISTS Jordan_pass_table (
                pass_id TEXT PRIMARY KEY,
                user_id INTEGER,
                visa_reference_no TEXT,
                jordan_pass_expiration_date TEXT,
                jordan_pass_active_status TEXT,
                FOREIGN KEY (user_id) REFERENCES User_table(user_id) ON DELETE CASCADE,
                FOREIGN KEY (visa_reference_no) REFERENCES Visa_table(reference_no) 
            );
        """

        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self.cursor.execute(execution_query)
        self.connect.commit()

        print("Jordan pass table has been created successfully...")

    # ================================== insertion a record ====================================

    def insert_user_info(self, email : str, password_hash : str, full_name : str, nationality : str, language : str, phone : str, role : str, user_verification_status : bool, avatar_url : str, created_at : str, updated_at : str) -> int :
        """
        :param email: string datatype
        :param password_hash: string datatype
        :param full_name: string datatype
        :param nationality: string datatype
        :param language: string datatype (ar / en)
        :param phone: string datatype
        :param role:
        :param user_verification_status: boolean datatype, sqlite doesn't support boolean will be converted into numbers
        :param avatar_url: string datatype,
        :param created_at: string datatype, sqlite doesn't support timestamp
        :param updated_at: string datatype, sqlite doesn't support timestamp
        :return: None datatype
        """
        user_verification_status = user_verification_status_convert(user_verification_status)

        execution_query = """--sql
                        INSERT INTO User_table (
                            email, 
                            password_hash, 
                            full_name, 
                            nationality, 
                            language, 
                            phone, 
                            role, 
                            user_verification_status, 
                            avatar_url, 
                            created_at, 
                            updated_at
                        ) 
                        VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """
        query_parameters = (email, password_hash, full_name, nationality, language, phone, role, user_verification_status, avatar_url, created_at, updated_at)

        try:
            self.cursor.execute(execution_query, query_parameters)
            self.connect.commit()
            print("A User record has been insert successfully...")
            return self.cursor.lastrowid

        except Exception as message:
            raise ValueError (f"Database Error: {message}")

    def insert_passport_info(self, passport_id : str, user_id : int, full_name_passport : str, passport_expiration_date : str) -> None:
        """
        :param passport_id: a string datatype (Primary key)
        :param user_id: an integer datatype (Foreign key)
        :param full_name_passport: a string datatype
        :param passport_expiration_date: a string datatype (sqlite doesn't support the date datatype)
        :return: None
        """
        execution_query = """--sql
                       INSERT INTO Passport_table VALUES (?, ?, ?, ?);
                   """
        query_parameters = (passport_id, user_id, full_name_passport, passport_expiration_date)

        try:
            self.cursor.execute(execution_query, query_parameters)
            self.connect.commit()
            print("A Passport record has been insert successfully...")

        except Exception as message:
            raise ValueError (f"Database Error: {message}")

    def insert_visa_info(self, reference_no: str, user_id : int, passport_id : str, visa_type : str, purpose_of_visit : str, arrival_date : str, departure_date : str, visa_application_status : str) -> None:

        """
        :param reference_no: string datatype (primary key)
        :param user_id: int datatype (Foreign key)
        :param passport_id: string datatype (Foreign key)
        :param visa_type: string datatype
        :param purpose_of_visit: string datatype
        :param arrival_date: string datatype
        :param departure_date: string datatype
        :param visa_application_status: string datatype
        :return: None
        """
        execution_query = """ --sql
                        INSERT INTO Visa_table VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """
        query_parameters = (reference_no, user_id, passport_id, visa_type, purpose_of_visit, arrival_date,
                            departure_date, visa_application_status)

        try:
            self.cursor.execute(execution_query, query_parameters)
            self.connect.commit()
            print("A Visa record has been inserted successfully...")

        except Exception as message:
            raise ValueError (f"Database Error: {message}")

    def insert_jordan_pass_info(self, pass_id : str, user_id : int, visa_reference_no : str, jordan_pass_expiration_date : str, jordan_pass_active_status : str) -> None:
        try:
            execution_query = """--sql
                INSERT INTO Jordan_pass_table VALUES (?, ?, ?, ?, ?);
            """
            query_parameters = (pass_id, user_id, visa_reference_no, jordan_pass_expiration_date, jordan_pass_active_status)

            self.cursor.execute(execution_query, query_parameters)
            self.connect.commit()

            print("A Jordan pass record has been inserted successfully...")

        except Exception as message:
            raise ValueError (f"Database Error: {message}")

    # ============================ Updating a table ======================================

    def update_user_table(self, user_id : int, **kwargs) -> None:
        """
        :param user_id: The primary key for searching in the required record
        :param kwargs: the required attributers for updating except the user_id
        :return: None
        """
        protected_attr = ["user_id"]
        try:
            for attr in kwargs:
                if attr in protected_attr:
                    print("Warning: You can not update the Primary key")
                    continue
                if attr == "user_verification_status":
                    kwargs[attr] = user_verification_status_convert(kwargs[attr])
                execution_query = f"""--sql
                    UPDATE User_table SET {attr} = ? WHERE user_id = ?;
                """
                query_parameters =(kwargs[attr], user_id)

                self.cursor.execute(execution_query, query_parameters)

            self.connect.commit()

            print("User table has been updated successfully...")

        except Exception as message:
            raise ValueError (f"{message}")

    def update_passport_table(self, passport_id : str, **kwargs) -> None:

        """
        :param passport_id: The primary key for searching on the required record (string datatype)
        :param kwargs: The required attributers for updating except the passport_id, user_id
        :return: None
        """

        protect_attr = ["passport_id", "user_id"]
        try:
            for attr in kwargs:
                if attr in protect_attr:
                    print("Warning: you can not update a primary key or foreign key")
                    continue

                execution_query = f"""--sql
                    UPDATE Passport_table SET {attr} = ? WHERE passport_id = ?;
                """

                query_parameters = (kwargs[attr], passport_id)

                self.cursor.execute(execution_query, query_parameters)

            self.connect.commit()

            print("Passport table has been updated successfully...")

        except Exception as message:
            raise ValueError (f"{message}")

    def update_visa_table(self, reference_no : str, **kwargs) -> None:

        """
        :param reference_no: The primary key for searching on the required record (string datatype)
        :param kwargs: The required attributers for updating except the user_id, passport_id
        :return: None
        """

        protect_attr = ['reference_no', 'user_id', 'passport_id']

        try:
            for attr in kwargs:

                if attr in protect_attr:
                    print("Warning: you can not update a Primary key or Foreign key")
                    continue

                execution_query = f"""--sql
                    UPDATE Visa_table set {attr} = ? WHERE reference_no = ?;
                """
                query_parameters = (kwargs[attr], reference_no)

                self.cursor.execute(execution_query, query_parameters)

            self.connect.commit()

            print("Visa table has been updated successfully...")

        except Exception as message:
            raise ValueError (f"{message}")

    def update_jordan_pass_table(self, pass_id : str, **kwargs) -> None:
        """
        :param pass_id:The primary key for searching on the required record (string datatype)
        :param kwargs: The required attributers for updating except the pass_id, user_id, visa_reference_no
        :return: None
        """

        protect_attr = ['pass_id', 'visa_reference_no', 'user_id']

        try:
            for attr in kwargs:

                if attr in protect_attr:
                    print("Warning you can not updating a Primary key or a Foreign key")
                execution_query = f"""--sql
                    UPDATE Jordan_pass_table SET {attr} = ? WHERE pass_id = ?;
                """

                query_parameters = (kwargs[attr], pass_id)

                self.cursor.execute(execution_query, query_parameters)

            self.connect.commit()

            print("Jordan pass table has been updated successfully...")

        except Exception as message:
            raise ValueError (f"{message}")

    # ======================= get a record ============================================

    def get_record_user_table(self, user_id : int) -> list:

        """
        :param user_id: (int) The primary key to get the record
        :return: (list) that contain the value of the record
        """

        #record = []
        execution_query = """--sql
            SELECT * FROM User_table WHERE user_id = ?;
        """
        query_parameters = (user_id, )

        try:
            self.cursor.execute(execution_query, query_parameters)
            record = self.cursor.fetchone()

            if record is None:
                raise ValueError(f"Record with ID {user_id} does not exist.")

        except Exception as message:
            raise ValueError (f"Database Error: {message}")

        return record

    def get_record_passport_table(self, passport_id : str) -> list:

        """
                :param passport_id: (str) The primary key to get the record
                :return: (list) that contain the value of the record
                """

        #record = []
        execution_query = """--sql
                    SELECT * FROM Passport_table WHERE passport_id = ?;
                """
        query_parameters = (passport_id,)

        try:
            self.cursor.execute(execution_query, query_parameters)
            record = self.cursor.fetchone()

            if record is None:
                raise ValueError(f"Record with ID {passport_id} does not exist.")

        except Exception as message:
            raise ValueError(f"Database Error: {message}")

        return record

    def get_record_visa_table(self, reference_id : str) -> list:

        """
        :param reference_id: (str) The primary key to get the record
        :return: (list) that contain the value of the record
        """

        #record = []
        execution_query = """--sql
                    SELECT * FROM Visa_table WHERE reference_no = ?;
                """
        query_parameters = (reference_id,)

        try:
            self.cursor.execute(execution_query, query_parameters)
            record = self.cursor.fetchone()

            if record is None:
                raise ValueError(f"Record with ID {reference_id} does not exist.")

        except Exception as message:
            raise ValueError(f"Database Error: {message}")

        return record

    def get_record_jordan_pass_table(self, pass_id : str) -> list:

        """
        :param pass_id: (str) The primary key to get the record
        :return: (list) that contain the value of the record
        """

        #record = []
        execution_query = """--sql
                    SELECT * FROM Jordan_pass_table WHERE pass_id = ?;
                """
        query_parameters = (pass_id,)

        try:
            self.cursor.execute(execution_query, query_parameters)
            record = self.cursor.fetchone()

            if record is None:
                raise ValueError(f"Record with ID {pass_id} does not exist.")

        except Exception as message:
            raise ValueError(f"Database Error: {message}")

        return record

    # =============================  deleting a record ====================================
    def delete_record_jordan_pass_table(self, pass_id : str) -> None:
        """
        :param pass_id: to select the required record
        :return: None
        """

        execution_query = """--sql
            DELETE FROM Jordan_pass_table WHERE pass_id = ?; 
        """
        query_parameters = (pass_id,)

        try:
            self.cursor.execute(execution_query, query_parameters)
            self.connect.commit()

            print(f"Record with from Jordan pass table ID {pass_id} have been deleted successfully...")
        except Exception as message:
            raise ValueError (f"Database Error: {message}")

    def delete_record_visa_table(self, reference_no : str) -> None:


        execution_query = """--sql
                DELETE FROM Visa_table WHERE reference_no = ?;
        """
        query_parameters = (reference_no,)

        try:
            self.__change_visa_foreign_key(reference_no)
            self.cursor.execute(execution_query, query_parameters)
            self.connect.commit()

            print(f"Record from Visa table with ID {reference_no} have been deleted successfully... ")

        except Exception as message:
            raise ValueError (f"Database Error: {message}")

    def delete_record_passport_table(self, passport_id : str) -> None:

        execution_query = """--sql
            DELETE FROM Passport_table WHERE passport_id = ?; 
        """
        query_parameters = (passport_id,)

        try:
            self.__change_passport_foreign_key(passport_id)
            self.cursor.execute(execution_query, query_parameters)
            self.connect.commit()

            print(f"Record from Passport table with ID {passport_id} have been deleted successfully... ")

        except Exception as message:
            raise ValueError(f"Database Error: {message}")

    def delete_record_user_table(self, user_id) -> None:

        execution_query = """--sql
            DELETE FROM User_table where user_id = ?;
        """
        query_parameters = (user_id, )

        try:
            #
            self.cursor.execute(execution_query, query_parameters)
            self.connect.commit()

            print(f"Record from User table with ID {user_id} have been deleted successfully... ")

        except Exception as message:
            raise ValueError (f"Database Error: {message}")
    # ========================== Handling deleting rows ==================================
    def __change_visa_foreign_key(self, visa_reference_no) -> None:

        execution_query = """--sql 
            UPDATE Jordan_pass_table SET visa_reference_no = NULL WHERE visa_reference_no = ? ;
        """

        query_parameters = (visa_reference_no, )
        try:
            self.cursor.execute(execution_query, query_parameters)
            self.connect.commit()

            print(f"\tThe foreign key visa_reference in the jordan_pass is updated to NULL")

        except Exception as message:
            raise ValueError (f"Database Error: {message}")

    def __change_passport_foreign_key(self, passport_id) -> None:

        execution_query = """--sql
            UPDATE Visa_table SET passport_id = NULL WHERE passport_id = ?;
        """
        query_parameters = (passport_id, )

        try:
            self.cursor.execute(execution_query, query_parameters)
            self.connect.commit()

            print(f"\tThe foreign key passport_id in the Visa table is updated to NULL")

        except Exception as message:
            raise ValueError (f"Database Error: {message}")

    def __deleting_user_foreign_key(self,user_id) -> None:

        execution_query = """--sql
            DELETE FROM User_table WHERE user_id = ?;
        """
        query_parameters = (user_id, )

        try:
            self.cursor.execute(execution_query, query_parameters)
            self.connect.commit()
            return self.cursor.lastrowid

        except Exception as message:
            raise ValueError (f"Database Error: {message}")


    # =========================== Sync Queue ==============================================



    def create_sync_queue_table(self) -> None:

        execution_query = """--sql
            CREATE TABLE IF NOT EXISTS Sync_queue_table 
            ( 
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                action TEXT NOT NULL, 
                payload TEXT NOT NULL, 
                status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'synced', 'failed')), 
                retry_count INTEGER DEFAULT 0, 
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            ); 
        """

        try:
            self.cursor.execute(execution_query)
            self.connect.commit()
            print("Sync queue table created successfully...")

        except Exception as message:
            raise ValueError(f"Database Error: {message}")

    def insert_action_sync_queue(self, action: str, payload: dict) -> int:

        execution_query = """--sql
            INSERT INTO Sync_queue_table (action, payload)
            VALUES (?, ?); 
        """

        query_parameters = (action, json.dumps(payload))

        try:
            self.cursor.execute(execution_query, query_parameters)
            self.connect.commit()

            action_id = self.cursor.lastrowid
            print("Action saved in Sync queue successfully...")

            return action_id

        except Exception as message:
            raise ValueError(f"Database Error: {message}")

    def get_pending_actions(self) -> list:

        execution_query = """--sql
            SELECT * FROM Sync_queue_table WHERE status = 'pending';
        """

        try:
            self.cursor.execute(execution_query)
            return self.cursor.fetchall()

        except Exception as message:
            raise ValueError(f"Database Error: {message}")

    def get_failed_actions(self) -> list:

        execution_query = """--sql
            SELECT * FROM Sync_queue_table WHERE status = 'failed'; 
        """

        try:
            self.cursor.execute(execution_query)
            return self.cursor.fetchall()

        except Exception as message:
            raise ValueError(f"Database Error: {message}")

    def update_sync_status(self, action_id: int, status: str) -> None:

        execution_query = """--sql
            UPDATE Sync_queue_table SET status = ? WHERE id = ?; 
        """

        try:
            self.cursor.execute(execution_query, (status, action_id))
            self.connect.commit()

        except Exception as message:
            raise ValueError(f"Database Error: {message}")

    def mark_action_in_progress(self, action_id: int) -> None:
        self.update_sync_status(action_id, 'in_progress')

    def mark_action_synced(self, action_id: int) -> None:
        self.update_sync_status(action_id, 'synced')

    def mark_action_failed(self, action_id: int) -> None:
        self.update_sync_status(action_id, 'failed')

    def increment_retry(self, action_id: int) -> None:

        execution_query = """--sql
            UPDATE Sync_queue_table SET retry_count = retry_count + 1 WHERE id = ?; 
        """

        try:
            self.cursor.execute(execution_query, (action_id,))
            self.connect.commit()

        except Exception as message:
            raise ValueError(f"Database Error: {message}")

    def delete_synced_actions(self) -> None:

        execution_query = """--sql
            DELETE FROM Sync_queue_table WHERE status = 'synced'; 
        """

        try:
            self.cursor.execute(execution_query)
            self.connect.commit()

        except Exception as message:
            raise ValueError(f"Database Error: {message}")

    def sync_all_actions(self) -> None:

        actions = self.get_pending_actions() + self.get_failed_actions()

        for action in actions:
            action_id = action[0]
            action_type = action[1]
            payload = json.loads(action[2])

            try:
                self.mark_action_in_progress(action_id)

                print(f"Syncing: {action_type} with payload: {payload}")

                self.mark_action_synced(action_id)

            except Exception:
                self.increment_retry(action_id)
                self.mark_action_failed(action_id)

    # =========================== Closing and Deleting ====================================

    def close_connection(self) -> None:
        self.connect.close()
        print("Connection to the database have been closed ...")

    @staticmethod
    def deleting_database() -> None:

        if os.path.exists(FILE_PATH):
            os.remove(FILE_PATH)
            print(f"{FILE_PATH} have been removed successfully... ")
        else:
            raise FileNotFoundError(f"{FILE_PATH} is not found!")
