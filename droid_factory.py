"""
Author: Grayson Olin
File: droid_factory.py
Language: Python 3
Date Created: 4/1/21
Last Modified: 4/2/21

The Trade Federation has plans to invade Naboo and require a droid army. With
the assistance of this program the Trade Federation will see that its droid
army is built and assembled to help protect their assets.
"""
from dataclasses import dataclass
import cs_queue as cq

@dataclass
class Droid:
    """
    Droid object with head, body, arms, legs, and a serial number.
    """
    head: bool
    body: bool
    arms: bool
    legs: bool
    serial: int

    def is_assembled(self):
        """
        Checks to see if the droid is completely assembled.

        :return: Boolean, whether or not the droid is built.
        """
        if (self.head and self.body and self.arms and self.legs) == True:
            return True
        else:
            return False

def conveyor_belt(filename):
    """
    Creates a conveyor belt in the form of a queue from a given file.

    :param filename: String, name of file.
    :return: Queue object filled with file contents named belt.
    """
    belt = cq.Queue(0, None, None)
    with open(filename, 'r') as file:
        for lines in file:
            cq.enqueue(belt, lines.strip())
    return belt

def build_droid(serial, belt):
    """
    Builds one droid.

    :param serial: Integer, the serial number of the droid being built.
    :param belt: Queue object, the conveyor belt containing the parts.
    :return: None
    """
    print("Building droid with serial number:", serial)
    droid = Droid(False, False, False, False, serial)
    while not droid.is_assembled():
        if cq.front(belt) == "head" and droid.head == False:
            droid.head = True
            cq.dequeue(belt)
            print("Head attached")
        elif cq.front(belt) == "body" and droid.body == False:
            droid.body = True
            cq.dequeue(belt)
            print("Body attached")
        elif cq.front(belt) == "arms" and droid.arms == False:
            droid.arms = True
            cq.dequeue(belt)
            print("Arms attached")
        elif cq.front(belt) == "legs" and droid.legs == False:
            droid.legs = True
            cq.dequeue(belt)
            print("Legs attached")
        else:
            print("Unnecessary part returned:", cq.front(belt))
            cq.enqueue(belt, cq.front(belt))
            cq.dequeue(belt)
    print("Droid", droid.serial, "assembled\n")

def build_droid_army(belt):
    """
    Builds as many droids as possible given parts.

    :param belt: Queue object, contains the parts.
    :return: None
    """
    serial = 10001
    while not cq.is_empty(belt):
        build_droid(serial, belt)
        serial += 1

def main():
    """
    Asks for file name for parts from user, builds the conveyor belt, and
    then the droid army.

    :return: None
    """
    filename = input("Enter parts file name: ")
    belt = conveyor_belt(filename)
    build_droid_army(belt)

if __name__ == '__main__':
    main()