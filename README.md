# Sign Language Data Collector

This project allows you to collect data for a custom sign language recognition system. It utilizes MediaPipe to extract 21 hand landmarks, which helps significantly increase the accuracy of downstream machine learning models by removing background noise and isolating structure.

## Overview
The script creates a divided 1680x1050 monitor with 4 distinct parts per your request:
1. **Webcam Capture:** Your standard webcam view with live overlay structure.
2. **Hand Sign Structure:** The extracted 21-point structure drawn over a solid black background.
3. **Reference Image:** Shows an image from `reference_images/` representing the target sign.
4. **Information Output:** Displays the current alphabet, save counts, and controls.

## Prerequisites
Install the required packages using:
```bash
pip install -r requirements.txt
```

## How to use
1. Run the data collector script:
   ```bash
   python data_collector.py
   ```
2. **UI Layout:** The window will show 4 quadrants as requested.
3. **Change Alphabet:** Press any key from `'A'` to `'Z'` to switch the selected alphabet.
4. **Save Image:** Press `'S'` to capture and save the current hand sign diagram. The script automatically crops the black-background structure, normalizes it to a 300x300 square, and saves it in `database/<alphabet>/`.
5. **Add References (Optional):** Put reference images (e.g., A.jpg, B.jpg) in the `reference_images` folder so that they appear when you select the corresponding letter.
6. **Quit:** Press `'Q'` parameter to safely terminate the script.

## Database Structure
Saved images are the 21-point skeletal structures of your hand, not the distracting real-world pixel data. This structured format heavily decreases variability during training datasets!
