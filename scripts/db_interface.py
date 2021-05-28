from tkinter import *
from tkinter import messagebox, ttk
import datetime
from tkinter.ttk import Treeview

from date_entry_widget import *
from db_functions import *
from tkcalendar import DateEntry

TK_SILENCE_DEPRECATION = 1

DATABASE = "TestDB.db"
ROOT_WIDTH = 800
ROOT_HEIGHT = 380
COUNTRY_DEFAULT_TEXT = "Select a country"

root = Tk()
root.title("SimpleDB")
root.geometry(str(ROOT_WIDTH) + "x" + str(ROOT_HEIGHT))
root.resizable(False, False)
style = ttk.Style(root)

# Connect to the database and create the cursor
conn = create_connection(DATABASE)
c = conn.cursor()

countries_records = query_db(conn, "SELECT * FROM COUNTRY")
countries = []
for country in countries_records:
    countries.append(country[2])

INT_CONDITIONS = ["=", "<", ">", "<=", ">=", "<>", "is between"]
STR_CONDITIONS = ["is", "starts with", "ends with", "contains", "doesn't start with", "doesn't end with",
                  "doesn't contain"]
CTR_CONDITIONS = ["is", "is not"]

CLIENT_KEYS = ('UID', 'First_Name', 'Last_Name', 'Country_ID', 'Invoice_Date')


# Functions
def clear_all_fields():
    cl_f_name.delete(0, END)
    cl_l_name.delete(0, END)
    client_country.set(COUNTRY_DEFAULT_TEXT)
    cl_cal1.delete(0, END)
    cl_cal2.delete(0, END)
    cl_uid1.delete(0, END)
    cl_uid2.delete(0, END)


def delete():
    conn_delete = create_connection(DATABASE)

    cur_item = query_tree.focus()
    cur_select = query_tree.item(cur_item)

    sel = grab_selection(cur_select)

    try:
        delete_values(conn_delete, "CLIENTS", sel["id"])
        clear_all_fields()
        query()
    except Error:
        messagebox.showwarning("Deletion failed!", "That is not a valid UID!")

    conn_delete.commit()
    conn_delete.close()


def update():
    conn_update = create_connection(DATABASE)

    val = grab_values()
    formatted_values = (
        val["first_name"]["value"], val["last_name"]["value"], val["country_id"]["value"], val["invoice_date"]["value"],
        val["id"]["value"])

    # Validating that all required fields are entered
    warning = validate_fields(val, True)

    if warning != "":
        messagebox.showwarning("Submission Error!", warning)
    else:
        try:
            update_value(conn_update, formatted_values)
            clear_all_fields()
            query()
        except Error:
            messagebox.showwarning("Submission Error!", "The client was not updated.")

    conn_update.commit()
    conn_update.close()


def add_new():
    conn_add = create_connection(DATABASE)

    val = grab_values()
    formatted_values = (
    val["first_name"]["value"], val["last_name"]["value"], val["country_id"]["value"], val["invoice_date"]["value"])
    warnings = ""

    # Validating that all required fields are entered
    warning = validate_fields(val, False)

    if warning != "":
        messagebox.showwarning("Submission Error!", warning)
    else:
        try:
            add_entry(conn_add, formatted_values)
            clear_all_fields()
            query()
        except Error:
            messagebox.showwarning("Submission Error!", "The user was not updated.")

    conn_add.commit()
    conn_add.close()


def validate_fields(val, uid_required):
    warnings = ""
    if val["first_name"]["value"] == "" or val["last_name"]["value"] == "":
        warnings += "All clients must have a first and last name\n"
    if client_country.get() == COUNTRY_DEFAULT_TEXT:
        warnings += "All clients must have an associated country\n"
    if val["id"]["value"] == "" and uid_required:
        warnings += "No UID selected!\n"

    return warnings


def grab_selection(cur_select):
    selected_values = {
        "id": cur_select['values'][0],
        "first_name": cur_select['values'][1],
        "last_name": cur_select['values'][2],
        "country": {
            "country_id": str(countries.index(cur_select['values'][3]) + 1),
            "country_name": cur_select['values'][3]
        },
        "invoice_date": {
            "month": cur_select["values"][4][0:2],
            "day": cur_select["values"][4][3:5],
            "year": cur_select["values"][4][6:],
        }
    }

    return selected_values


def copy_selection(a):
    def update_field(field, new_value):
        field.delete(0, END)
        field.insert(0, new_value)

    cur_item = query_tree.focus()
    cur_select = query_tree.item(cur_item)

    sel = grab_selection(cur_select)
    date_entry1 = [sel["invoice_date"]["month"], sel["invoice_date"]["day"], sel["invoice_date"]["year"]]

    update_field(cl_f_name, sel["first_name"])
    update_field(cl_l_name, sel["last_name"])
    client_country.set(sel["country"]["country_name"])
    update_field(cl_cal1, date_entry1)
    update_field(cl_cal2, ["", "", ""])
    update_field(cl_uid1, sel["id"])
    update_field(cl_uid2, "")

    print(cur_select)
    print(a)


def build_query(key, values, is_first_criteria):
    # Start by checking if the user wants to use this key as a criteria
    if values["value"] == "":
        return None
    else:
        query_string = ""
        cond = values["cond"]
        value = values["value"]
        if "comparison" in values:
            comparison = values["comparison"]
        else:
            comparison = ""

        # Now check if this is the first condition. If it is, add "WHERE"
        if is_first_criteria:
            query_string += " WHERE "
        else:
            query_string += " AND "

        cond_dict = {
            "is": f'{key} IS "{value}"',
            "is not": f'{key} IS NOT {value}',
            "starts with": f'{key} LIKE "{value}%"',
            "ends with": f'{key} LIKE "%{value}"',
            "contains": f'{key} LIKE "%{value}%"',
            "doesn't start with": f'{key} NOT LIKE "{value}%"',
            "doesn't end with": f'{key} NOT LIKE "%{value}"',
            "doesn't contain": f'{key} NOT LIKE "%{value}%"',
            "is between": f'{key} BETWEEN "{value}" AND "{comparison}"'
        }
        query_string += cond_dict.get(cond, f'{key} {cond} "{value}"')

        return query_string


def grab_values():
    def date_to_string(date_list):
        if date_list == ["", "", ""]:
            return ""
        else:
            month = date_list[0]
            day = date_list[1]
            year = date_list[2]
            date_string = year + month + day
            return date_string

    def int_to_str(int_value):
        if int_value == "":
            return ""
        else:
            return str(int_value)

    date1_str = date_to_string(cl_cal1.get())
    date2_str = date_to_string(cl_cal2.get())

    if client_country.get() == COUNTRY_DEFAULT_TEXT:
        country_value = ""
    else:
        country_value = str(countries.index(client_country.get()) + 1)

    uid1 = int_to_str(cl_uid1.get())
    uid2 = int_to_str(cl_uid2.get())

    query_values = {
        "first_name": {
            "value": cl_f_name.get(),
            "cond": cl_f_name_cond_value.get()
        },
        "last_name": {
            "value": cl_l_name.get(),
            "cond": cl_l_name_cond_value.get()
        },
        "country_id": {
            "value": country_value,
            "cond": cl_country_cond_value.get()
        },
        "invoice_date": {
            "value": date1_str,
            "comparison": date2_str,
            "cond": cl_cal_cond_value.get()
        },
        "id": {
            "value": uid1,
            "comparison": uid2,
            "cond": cl_uid_cond_value.get()
        },
    }

    return query_values


def query():
    print("Beginning query now!")
    conn_query = create_connection(DATABASE)

    query_str = "SELECT * FROM CLIENTS"

    query_values = grab_values()
    is_first_criteria = True
    for value in query_values:
        query_piece = build_query(value, query_values[value], is_first_criteria)
        if query_piece:
            print(query_piece)
            is_first_criteria = False
            query_str += query_piece
        else:
            print("You are not querying " + value)
    print(query_str)
    query_result = query_db(conn_query, query_str)
    print(query_result)

    query_tree.delete(*query_tree.get_children())

    reformatted_results = []
    for client in query_result:
        country_value = countries[int(client[3]) - 1]
        date_value = f'{client[4][4:6]}/{client[4][6:]}/{client[4][:4]}'
        reformatted_client = (client[0], client[1], client[2], country_value, date_value)
        reformatted_results.append(reformatted_client)
    for result in reformatted_results:
        query_tree.insert("", "end", values=result)

    conn_query.commit()
    conn_query.close()


def disable_extra_fields(*args):
    date_cond = cl_cal_cond_value.get()
    uid_cond = cl_uid_cond_value.get()
    enabling_value = "is between"

    if date_cond != enabling_value:
        cl_cal2.delete(0, END)
        cl_cal2.set_state("disabled")
    else:
        cl_cal2.set_state("normal")

    if uid_cond != enabling_value:
        cl_uid2.delete(0, END)
        cl_uid2.config(state="disabled")
    else:
        cl_uid2.config(state="normal")


# Creating the GUI
cl_f_name_cond_value = StringVar(root, value="is")
cl_f_name_label = Label(root, text="First Name")
cl_f_name_label.grid(column=0, row=0, columnspan=2, padx=(5, 0), pady=(10, 0), sticky="W")
cl_f_name_cond = OptionMenu(root, cl_f_name_cond_value, *STR_CONDITIONS)
cl_f_name_cond.grid(column=2, row=0, columnspan=2, pady=(10, 0), sticky="NESW")
cl_f_name = Entry(root)
cl_f_name.grid(column=4, row=0, columnspan=4, pady=(10, 0), sticky="NESW")

cl_l_name_cond_value = StringVar(root, value="is")
cl_l_name_label = Label(root, text="Last Name")
cl_l_name_label.grid(column=0, row=1, columnspan=2, padx=(5, 0), sticky="W")
cl_l_name_cond = OptionMenu(root, cl_l_name_cond_value, *STR_CONDITIONS)
cl_l_name_cond.grid(column=2, row=1, columnspan=2, sticky="NESW")
cl_l_name = Entry(root)
cl_l_name.grid(column=4, row=1, columnspan=4, sticky="NESW")

cl_country_cond_value = StringVar(root, value="is")
client_country = StringVar(root, value=COUNTRY_DEFAULT_TEXT)
cl_country_label = Label(root, text="Country")
cl_country_label.grid(column=0, row=2, columnspan=2, padx=(5, 0), sticky="W")
cl_country_cond = OptionMenu(root, cl_country_cond_value, *CTR_CONDITIONS)
cl_country_cond.grid(column=2, row=2, columnspan=2, sticky="NESW")
cl_country = OptionMenu(root, client_country, COUNTRY_DEFAULT_TEXT, *countries)
cl_country.grid(column=4, row=2, columnspan=4, sticky="NESW")

cl_cal_cond_value = StringVar(root, value="is between")
cl_cal_label = Label(root, text="Invoice date")
cl_cal_label.grid(column=0, row=3, columnspan=2, padx=(5, 0), sticky="W")
cl_cal_cond = OptionMenu(root, cl_cal_cond_value, *INT_CONDITIONS, command=disable_extra_fields)
cl_cal_cond.grid(column=2, row=3, columnspan=2, sticky="NESW")
cl_cal1_frame = Frame(root)
cl_cal1_frame.grid(column=4, row=3, columnspan=2)
cl_cal1 = DateEntryBetter(cl_cal1_frame, sticky="NESW")
cl_cal1.pack(side=LEFT)
cl_cal2_frame = Frame(root)
cl_cal2_frame.grid(column=6, row=3, columnspan=2)
cl_cal2 = DateEntryBetter(cl_cal2_frame, sticky="NESW")
cl_cal2.pack(side=LEFT)

cl_uid_cond_value = StringVar(root, value="=")
cl_uid_label = Label(root, text="Client ID")
cl_uid_label.grid(column=0, row=4, columnspan=2, padx=(5, 0), sticky="W")
cl_uid_cond = OptionMenu(root, cl_uid_cond_value, *INT_CONDITIONS, command=disable_extra_fields)
cl_uid_cond.grid(column=2, row=4, columnspan=2, sticky="NESW")
cl_uid1 = Entry(root)
cl_uid1.grid(column=4, row=4, columnspan=2, sticky="NESW")
cl_uid2 = Entry(root, state='disabled')
cl_uid2.grid(column=6, row=4, columnspan=2, sticky="NESW")

clear_button = Button(root, text="Clear all fields", command=clear_all_fields)
clear_button.grid(column=8, row=0, columnspan=2, padx=10, pady=(10, 0), sticky="NESW")
submit_button = Button(root, text="Add new client to DB", command=add_new)
submit_button.grid(column=8, row=1, columnspan=2, padx=10, sticky="NESW")
update_button = Button(root, text="Update existing client by UID", command=update)
update_button.grid(column=8, row=2, columnspan=2, padx=10, sticky="NESW")
delete_button = Button(root, text="Delete existing client by UID", command=delete)
delete_button.grid(column=8, row=3, columnspan=2, padx=10, sticky="NESW")
query_button = Button(root, text="Find clients matching criteria", command=query)
query_button.grid(column=8, row=4, columnspan=2, padx=10, sticky="NESW")

query_tree = Treeview(root, columns=CLIENT_KEYS, show="headings")
for key in CLIENT_KEYS:
    query_tree.heading(key, text=key)
    query_tree.column(key, width=int((ROOT_WIDTH - 20) / len(CLIENT_KEYS)))
query_tree.grid(column=0, row=9, columnspan=10, padx=(10, 10), pady=(10, 10), sticky="NESW")
query_tree.bind('<ButtonRelease-1>', copy_selection)

# Commit changes and close the connection
conn.commit()
conn.close()

# Initialize the window
root.mainloop()
