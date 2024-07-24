import pickle  # Pickle library for serializing Python objects
import cv2  # OpenCV library for computer vision tasks
import cvzone
import numpy as np  # NumPy library for numerical operations
from cvzone.HandTrackingModule import HandDetector
import requests  # Library for making HTTP requests
import pytz  # Library for timezone conversions
from datetime import datetime  # Library for handling dates and times

######################################
cam_id = 1
width, height = 1920, 1080
map_file_path = "..\Step1–GetCornerPoints\map.p"
countries_file_path = "..\Step2_Create_Country_Polygons\countries.p"
geonames_username = "Mahdi1380"  # Replace with your Geonames API username
######################################

file_obj = open(map_file_path, 'rb')
map_points = pickle.load(file_obj)
file_obj.close()
print(f"Loaded map coordinates.")

# Load previously defined Regions of Interest (ROIs) polygons from a file
if countries_file_path:
    file_obj = open(countries_file_path, 'rb')
    polygons = pickle.load(file_obj)
    file_obj.close()
    print(f"Loaded {len(polygons)} countries.")
else:
    polygons = []

# Open a connection to the webcam
cap = cv2.VideoCapture(cam_id)  # For Webcam
# Set the width and height of the webcam frame
cap.set(3, width)
cap.set(4, height)
# Counter to keep track of how many polygons have been created
counter = 0

# Initialize the HandDetector class with the given parameters
detector = HandDetector(staticMode=False,
                        maxHands=1,
                        modelComplexity=1,
                        detectionCon=0.5,
                        minTrackCon=0.5)


def warp_image(img, points, size=[1920, 1080]):
    pts1 = np.float32([points[0], points[1], points[2], points[3]])
    pts2 = np.float32([[0, 0], [size[0], 0], [0, size[1]], [size[0], size[1]]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    imgOutput = cv2.warpPerspective(img, matrix, (size[0], size[1]))
    return imgOutput, matrix


def warp_single_point(point, matrix):
    point_homogeneous = np.array([[point[0], point[1], 1]], dtype=np.float32)
    point_homogeneous_transformed = np.dot(matrix, point_homogeneous.T).T
    point_warped = point_homogeneous_transformed[0, :2] / point_homogeneous_transformed[0, 2]
    return point_warped


def get_finger_location(img, imgWarped):
    hands, img = detector.findHands(img, draw=False, flipType=True)
    if hands:
        hand1 = hands[0]
        indexFinger = hand1["lmList"][8][0:2]
        warped_point = warp_single_point(indexFinger, matrix)
        warped_point = int(warped_point[0]), int(warped_point[1])
        print(indexFinger, warped_point)
        cv2.circle(imgWarped, warped_point, 5, (255, 0, 0), cv2.FILLED)
    else:
        warped_point = None
    return warped_point


def create_overlay_image(polygons, warped_point, imgOverlay):
    detected_country = None  # Variable to store the detected country name
    for item in polygons:
        if len(item) >= 2:
            polygon = item[0]
            name = item[1]
            polygon_np = np.array(polygon, np.int32).reshape((-1, 1, 2))
            result = cv2.pointPolygonTest(polygon_np, warped_point, False)
            if result >= 0:
                cv2.polylines(imgOverlay, [np.array(polygon)], isClosed=True, color=(0, 255, 0), thickness=2)
                cv2.fillPoly(imgOverlay, [np.array(polygon)], (0, 255, 0))
                cvzone.putTextRect(imgOverlay, name, polygon[0], scale=1, thickness=1)
                detected_country = name  # Update the detected country name
    return imgOverlay, detected_country


def inverse_warp_image(img, imgOverlay, map_points):
    map_points = np.array(map_points, dtype=np.float32)
    destination_points = np.array([[0, 0], [imgOverlay.shape[1] - 1, 0], [0, imgOverlay.shape[0] - 1],
                                   [imgOverlay.shape[1] - 1, imgOverlay.shape[0] - 1]], dtype=np.float32)
    M = cv2.getPerspectiveTransform(destination_points, map_points)
    warped_overlay = cv2.warpPerspective(imgOverlay, M, (img.shape[1], img.shape[0]))
    result = cv2.addWeighted(img, 1, warped_overlay, 0.65, 0, warped_overlay)
    return result


def get_timezone(country_name):
    """
    Get the timezone for the given country name using the REST Countries API.

    Parameters:
    - country_name: The name of the country.

    Returns:
    - timezone: The timezone of the country.
    """
    timezone = "N/A"
    try:
        response = requests.get(f"https://restcountries.com/v3.1/name/{country_name}")
        if response.status_code == 200:
            data = response.json()
            if data:
                timezone = data[0].get("timezones", ["N/A"])[0]
    except Exception as e:
        print(f"Error fetching timezone: {e}")

    return timezone

def get_country_info(country_name):
    """
    Get the capital, timezone, flag, population, and area of the country using the REST Countries API.

    Parameters:
    - country_name: The name of the country.

    Returns:
    - capital: The capital of the country.
    - timezone: The timezone of the country.
    - flag_url: The URL of the country's flag.
    - population: The population of the country.
    - area: The area of the country.
    """
    capital = "N/A"
    timezone = "N/A"
    flag_url = None
    population = "N/A"
    area = "N/A"
    try:
        # Fetch capital city, flag URL, population, and area from REST Countries API
        response = requests.get(f"https://restcountries.com/v3.1/name/{country_name}")
        if response.status_code == 200:
            data = response.json()
            if data:
                capital = data[0].get("capital", ["N/A"])[0]
                timezone = data[0].get("timezones", ["N/A"])[0]
                flag_url = data[0].get("flags", {}).get("png")
                population = data[0].get("population", "N/A")
                area = data[0].get("area", "N/A")

    except Exception as e:
        print(f"Error fetching country info: {e}")

    return capital, timezone, flag_url, population, area

def download_flag(flag_url):
    """
    Download the flag image from the given URL and return it as an OpenCV image.

    Parameters:
    - flag_url: The URL of the flag image.

    Returns:
    - flag_img: The OpenCV image of the flag.
    """
    flag_img = None
    try:
        resp = requests.get(flag_url, stream=True).raw
        flag_img = np.asarray(bytearray(resp.read()), dtype="uint8")
        flag_img = cv2.imdecode(flag_img, cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"Error downloading flag image: {e}")

    return flag_img

while True:
    success, img = cap.read()
    imgWarped, matrix = warp_image(img, map_points)
    imgOutput = img.copy()
    warped_point = get_finger_location(img, imgWarped)
    h, w, _ = imgWarped.shape
    imgOverlay = np.zeros((h, w, 3), dtype=np.uint8)

    detected_country = None  # Initialize detected country name variable
    capital_city = "N/A"  # Initialize capital city variable
    timezone_info = "N/A"  # Initialize timezone info variable
    population = "N/A"  # Initialize population variable
    area = "N/A"  # Initialize area variable
    flag_img = None  # Initialize flag image variable

    if warped_point:
        imgOverlay, detected_country = create_overlay_image(polygons, warped_point, imgOverlay)
        imgOutput = inverse_warp_image(img, imgOverlay, map_points)
        if detected_country:
            capital_city, timezone_info, flag_url, population, area = get_country_info(detected_country)  # Fetch the capital city, timezone info, flag URL, population, and area
            if flag_url:
                flag_img = download_flag(flag_url)  # Download the flag image

    # Draw the gray box in the bottom left corner
    box_x, box_y, box_w, box_h = 0, height - 300, 400, 300
    cv2.rectangle(imgOutput, (box_x, box_y), (box_x + box_w, box_y + box_h), (169, 169, 169), cv2.FILLED)

    # Add text to the gray box

    cv2.putText(imgOutput, "INFORMATION", (box_x + 10, box_y + 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(imgOutput, "Country :", (box_x + 10, box_y + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    if detected_country:
        cv2.putText(imgOutput, str(detected_country), (box_x + 120, box_y + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(imgOutput, "Capital :", (box_x + 10, box_y + 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(imgOutput, str(capital_city), (box_x + 110, box_y + 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(imgOutput, "Timezone :", (box_x + 10, box_y + 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(imgOutput, str(timezone_info), (box_x + 140, box_y + 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(imgOutput, "Population :", (box_x + 10, box_y + 190), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(imgOutput, str(population), (box_x + 150, box_y + 190), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(imgOutput, "Area (km^2) :", (box_x + 10, box_y + 230), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(imgOutput, str(area), (box_x + 180, box_y + 230), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    # Display the flag image if available
    if flag_img is not None:
        flag_img_resized = cv2.resize(flag_img, (100, 60))  # Resize the flag image
        imgOutput[box_y + 20: box_y + 20 + flag_img_resized.shape[0], box_x + box_w - 120: box_x + box_w - 20] = flag_img_resized

    cv2.imshow("Output Image", imgOutput)

    key = cv2.waitKey(1)
    if key == 27:  # 27 is the ASCII code for the ESC key
        break

cap.release()
cv2.destroyAllWindows()
