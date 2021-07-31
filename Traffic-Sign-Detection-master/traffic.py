# By Roi Solomon
from sklearn.model_selection import train_test_split
import cv2
import numpy as np
import os
import sys
import tensorflow as tf


EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """

    images = []
    labels = []

    for dir1 in os.listdir(data_dir):
        folder_path = os.path.join(data_dir, dir1)
        if os.path.isdir(folder_path):
            print(
                f"The data is loadindg, currently lodaing from: {folder_path}...")
            for file in os.listdir(folder_path):
                image_path = os.path.join(data_dir, dir1, file)
                image = cv2.imread(image_path, cv2.COLOR_BGR2RGB)
                image = cv2.resize(image, (IMG_HEIGHT,
                                           IMG_WIDTH), interpolation=cv2.INTER_AREA)
                image = np.array(image)
                image = image.astype('float32')
                image /= 255
                images.append(image)
                labels.append(int(dir1))
    return images, labels


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    # Deploy convolutional neural network
    model = tf.keras.models.Sequential([

        # Learn 32 filters using a  grid of 3x3 kernel
        tf.keras.layers.Conv2D(
            32, (3, 3), activation="relu", input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)
        ),

        # Max-pooling layer
        tf.keras.layers.MaxPooling2D(pool_size=(3, 3)),

        # Tried dropout rates of : 0.5, 0.4, 0.3, --> 0.2
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dropout(0.2),

        # Hidden layer with dropout of 0.2
        tf.keras.layers.Dense(NUM_CATEGORIES * 32, activation="relu"),
        tf.keras.layers.Dropout(0.2),

        # Another hidden layer
        tf.keras.layers.Dense(NUM_CATEGORIES * 16, activation="relu"),

        # Another hidden layer
        tf.keras.layers.Dense(NUM_CATEGORIES * 8, activation="relu"),

        # Another hidden layer
        tf.keras.layers.Dense(NUM_CATEGORIES * 4, activation="relu"),

        # Add an output layer with output units for all categories
        tf.keras.layers.Dense(NUM_CATEGORIES, activation="softmax")
    ])

    # Training the model
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model


if __name__ == "__main__":
    main()
