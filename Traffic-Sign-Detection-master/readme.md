# Traffic - CS50 AI With Python

#### By Roi Solomon

I used the The German Traffic Sign Recognition Benchmark [(GTSRB)](http://benchmark.ini.rub.de/?section=gtsrb&subsection=news) database.

## What I Found?

    Tested the effects of hidden layers on the accuracy of the model.

### Hidden Layers:

```python

        # Another hidden layer
        tf.keras.layers.Dense(NUM_CATEGORIES * 16, activation="relu"),

        # Another hidden layer
        tf.keras.layers.Dense(NUM_CATEGORIES * 8, activation="relu"),

        # Another hidden layer
        tf.keras.layers.Dense(NUM_CATEGORIES * 4, activation="relu"),
```

## Result - 97% Acccuracy:

    

## GTSRB Database:

The database contains 43 subdirectories in this dataset, numbered 0 through 42. Each numbered subdirectory represents a different category (a different type of road sign). Within each traffic sign’s directory is a collection of images of that type of traffic sign.

[Download](https://cdn.cs50.net/ai/2020/x/projects/5/gtsrb.zip)

## Sources

- TensorFlow The Sequential model - [Link](https://www.tensorflow.org/guide/keras/sequential_model)
- Loading Custom Image Dataset for Deep Learning Models: Part 1 - [Link](https://towardsdatascience.com/loading-custom-image-dataset-for-deep-learning-models-part-1-d64fa7aaeca6)
- Understand the Softmax Function in Minutes - [Link](https://medium.com/data-science-bootcamp/understand-the-softmax-function-in-minutes-f3a59641e86d#:~:text=Softmax%20is%20an%20activation%20function.&text=Softmax%20is%20exponential%20and%20enlarges,encoded%20in%20one%20hot%20encoding)
- CS50 Lecture 5 Notes - [Link](https://cs50.harvard.edu/ai/2020/notes/5/)

## License

[MIT](https://choosealicense.com/licenses/mit/)
