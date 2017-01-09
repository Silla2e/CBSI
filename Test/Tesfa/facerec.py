import json
import os
import urllib.request


def return_data(url, api_key):
    request = urllib.request.Request(url)
    request.add_header('Authorization', 'Bearer {}'.format(api_key))

    response = urllib.request.urlopen(request)
    encoding = response.headers.get_content_charset()

    data = json.loads(response.read().decode(encoding))

    return data


def get_next_from_data(data):
    if 'paging' in data:
        paging = data['paging']
        if 'next' in paging:
            return paging['next']
        else:
            return None
    else:
        return None


def parse_images(data, user_id, picture_number):
    # Facebook defaults to returning 25 pictures
    for data_object in data:
        picture_url = data_object['source']
        f = open('{}.jpg'.format(picture_number), 'wb')
        f.write(urllib.request.urlopen(picture_url).read())
        f.close()

        # Increment picture number for each picture
        picture_number = picture_number + 1


def record_face_percentages_from_pictures(data, user_id, picture_number):
    face_coordinate_file = open('face_coordinates.txt', 'a')

    # Every data obj has 25 pictures in it
    for data_object in data:
        picture_tags = data_object['tags']['data']
        for data_tag in picture_tags:
            # FIXME: Not working correctly, getting too many tags
            # add in functionality to just get the id tags out
            if 'id' in data_tag:
                if data_tag['id'] == user_id:
                    x_face_coordinate = data_tag['x']
                    y_face_coordinate = data_tag['y']
                    face_coordinate_file.write(
                        "{},{},{}\n".format(picture_number,
                                            x_face_coordinate,
                                            y_face_coordinate))

        picture_number = picture_number + 1
    face_coordinate_file.close()


def main():
    # TODO: create face_coordinate file off the get go/ or something
    base_url = "https://graph.facebook.com/v2.3/"

    # super secret api password thingy!
    facebook_api_key = os.getenv('FACEBOOK_API_KEY')

    # Make dir for pcitures and change into that directory
    if not os.path.exists("pictures"):
        os.makedirs("pictures")
    os.chdir("pictures")

    # If this script is run multiple times, removes issues with appending coords
    if os.path.isfile('face_coordinates.txt'):
        os.remove('face_coordinates.txt')

    # This is getting out the user id!
    data = return_data(base_url + "me", facebook_api_key)
    # Will need id for parsing photo tags
    user_id = data['id']

    # This is getting out the first set of pictures!
    data = return_data(base_url + "me/photos", facebook_api_key)
    next_ = get_next_from_data(data)

    data = data['data']
    picture_number = 0
    parse_images(data, user_id, picture_number)
    record_face_percentages_from_pictures(data, user_id, picture_number)
    picture_number += len(data)
    print(len(data))

    if next_ is None:
        more_photos = False
    else:
        more_photos = True

    while (more_photos):
        data = return_data(next_, facebook_api_key)
        next_ = get_next_from_data(data)

        data = data['data']
        parse_images(data, user_id, picture_number)
        record_face_percentages_from_pictures(data, user_id, picture_number)

        picture_number += len(data)
        print(len(data))
        if next_ is None:
            more_photos = False

    print("Done!")


if __name__ == '__main__':
    main()
    import sys
    import os
    import csv
    import cv2


    def parse_face_coord_file(face_coord_txt_file=None):
        result = []
        if not face_coord_txt_file is None:
            with open(face_coord_txt_file, 'r') as csvfile:
                linereader = csv.reader(csvfile, delimiter=',', quotechar='\n')
                for index, x_coord, y_coord in linereader:
                    result.append((int(index), float(x_coord), float(y_coord)))
        return result


    def remove_face_coordinate(face_coordinate_list, index):
        """
        This method will actually delete the offending index from the
        `face_coordinate_list` and the underlying file. Note: this also
        assumes the file is in `pictures/face_coordinates.txt`
        """
        all_remaining_indexes = [int(x) for x in face_coordinate_list[0]]
        try:
            delete_me = all_remaining_indexes.index(index)
            face_coordinate_list.pop(delete_me)
            file = open('face_coordinates.txt', 'w')
            for pic_num, x_coord, y_coord in face_coordinate_list:
                file.write("{}, {}, {}\n".format(int(pic_num), x_coord, y_coord))

            file.close()
        except ValueError:
            pass


    def display_images(filenames, face_cascade, face_coordinate_list=None):
        for file in filenames:
            # Gets the index from the filename. Assumes filename is in form "123.jpg"
            index = int(file[:-4])
            # Reads the image out of the file
            cv_frame = cv2.imread(file)

            # Turns image from BGR (color scheme) into gray!
            gray_image = cv2.cvtColor(cv_frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray_image, 1.3, 5)
            print(faces)

            for (x, y, w, h) in faces:
                cv2.rectangle(cv_frame, (x, y), (w + w, y + h), (255, 0, 0), 2)

            # NOTE: This is the coordinates from facebook!
            if face_coordinate_list:
                image_height, image_width, _ = cv_frame.shape

                # Facebook keeps coords as percentages!
                if face_coordinate_list:
                    x_and_y_coordinates = face_coordinate_list[index][-2:]
                    if not x_and_y_coordinates[0] is None:
                        transformed_coords = (int(image_width / 100 * x_and_y_coordinates[0]),
                                              int(image_height / 100 * x_and_y_coordinates[1]))

                        cv2.circle(cv_frame, transformed_coords, 20, (255, 106, 255))

            while (True):
                # TODO: Quit out of this function logic add me?
                cv2.imshow('{}'.format(filenames[index]), cv_frame)

                key_pressed = cv2.waitKey(1)
                if key_pressed == 8:  # this is the `backspace` key
                    print("removing file {}.jpg".format(index))
                    os.remove('{}.jpg'.format(index))
                    if face_coordinate_list:
                        remove_face_coordinate(face_coordinate_list, index)
                    break
                elif key_pressed == 13:  # this is the `enter` key
                    break

            cv2.destroyWindow(filenames[index])


    if __name__ == '__main__':

        if not os.path.exists("pictures"):
            print("the pictures directory does not exist, have you run get_pictures_from_facebook.py yet?")
            sys.exit(-1)

        os.chdir('pictures')
        _, _, filenames = next(os.walk("."))
        if 'face_coordinates.txt' in filenames:
            face_coord_txt_index = filenames.index('face_coordinates.txt')
            face_coord_txt_file = filenames.pop(face_coord_txt_index)
        else:
            face_coord_txt_file = raw_input("Enter Text Coordinate File Name,\
                                            or hit enter if None")

            # Allow user to decide if using a face coordinate text file
            # TODO: Decide if hit enter if this is not iterable
            if len(face_coord_txt_file) < 1:
                face_coord_txt_file = None
        if face_coord_txt_file:
            face_coordinate_list = parse_face_coord_file(face_coord_txt_file)
        else:
            face_coordinate_list = None

        if not os.path.exists('../haarcascade_frontalface_default.xml'):
            print("Could not find haarcascade file!")

        face_cascade = cv2.CascadeClassifier('../haarcascade_frontalface_default.xml')
        # this functionality needs to be looped/changed
        print("Push `Enter` to continue to next image, `Backspace` will delete img")
        display_images(filenames, face_cascade, face_coordinate_list)

        cv2.destroyAllWindows()
