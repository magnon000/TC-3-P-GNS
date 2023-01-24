from tkinter import filedialog
import shelve


def ask_obj_path() -> str:  # no file type
    return filedialog.askopenfilename(title=u'Save Python persistent object', filetypes=[("DAT", ".dat")])[:-4]


# def charge_as():


if __name__ == '__main__':
    obj_path = ask_obj_path()
    print(obj_path)
    with shelve.open(obj_path) as test:
        obj_list = [ele for ele in test]
        print(obj_list)
        # for ele in test:
        #     print(ele)
        # print(test['asbr_as_2'])
        # print(test.keys())
