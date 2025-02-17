from __future__ import print_function
import keras
from keras.datasets import cifar10
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras.layers.normalization import BatchNormalization
import numpy as np
import os

import matplotlib.pyplot as plt

batch_size = 32
num_classes = 10
epochs = 10
data_augmentation = True
droping = True
batchNorm = True
num_predictions = 20
save_dir = os.path.join(os.getcwd(), 'saved_models')
model_name = 'keras_cifar10_trained_model.h5'

# The data, split between train and test sets:
(x_train, y_train), (x_test, y_test) = cifar10.load_data()
x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255
print('x_train shape:', x_train.shape)
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')

# Convert class vectors to binary class matrices.
mean = np.mean(x_train,axis=(0,1,2,3))
std = np.std(x_train,axis=(0,1,2,3))
x_train = (x_train-mean)/(std+1e-7)
x_test = (x_test-mean)/(std+1e-7)

y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)

model = Sequential()

# 1st Convolutional Layer
model.add(Conv2D(filters=48, input_shape=(32,32,3), kernel_size=(3,3), strides=(1,1), padding='same'))
model.add(Activation('relu'))
if batchNorm: model.add(BatchNormalization())

# Max Pooling
model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2)))
if droping: model.add(Dropout(0.2))

# 2nd Convolutional Layer
model.add(Conv2D(filters=96, kernel_size=(3,3), padding='same'))
model.add(Activation('relu'))
if batchNorm: model.add(BatchNormalization())

# Max Pooling
model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2)))
if droping: model.add(Dropout(0.3))

# 3rd Convolutional Layer
model.add(Conv2D(filters=192, kernel_size=(3,3), padding='same'))
model.add(Activation('relu'))
if batchNorm: model.add(BatchNormalization())

# 4th Convolutional Layer
model.add(Conv2D(filters=192, kernel_size=(3,3), padding='same'))
model.add(Activation('relu'))
if batchNorm: model.add(BatchNormalization())

# Max pooling
model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2)))
if droping: model.add(Dropout(0.4))

# 5th Convolutional Layer
model.add(Conv2D(filters=256, kernel_size=(3,3), padding='same'))
model.add(Activation('relu'))
if batchNorm: model.add(BatchNormalization())

# Max Pooling
model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2)))
if droping: model.add(Dropout(0.5))
# Passing it to a Fully Connected layer
model.add(Flatten())
# 1st Fully Connected Layer
model.add(Dense(512))
model.add(Activation('relu'))
if batchNorm: model.add(BatchNormalization())

# Add Dropout to prevent overfitting
# if dropout: model.add(Dropout(0.4))
# 2nd Fully Connected Layer
model.add(Dense(512))
model.add(Activation('relu'))
if batchNorm: model.add(BatchNormalization())
# Add Dropout
# if dropout: model.add(Dropout(0.4))

# 3rd Fully Connected Layer
model.add(Dense(256))
model.add(Activation('relu'))
if batchNorm: model.add(BatchNormalization())
# Add Dropout
# if dropout: model.add(Dropout(0.4))

# Output Layer
model.add(Dense(10))
model.add(Activation('softmax'))

# initiate RMSprop optimizer
opt = keras.optimizers.rmsprop(lr=0.0001, decay=1e-6)

# Let's train the model using RMSprop
model.compile(loss='categorical_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])

model.summary()

history = None
if not data_augmentation:
    print('Not using data augmentation.')
    history = model.fit(x_train, y_train,
              batch_size=batch_size,
              epochs=epochs,
              validation_data=(x_test, y_test),
              shuffle=True)
else:
    print('Using real-time data augmentation.')
    # This will do preprocessing and realtime data augmentation:
    datagen = ImageDataGenerator(
        featurewise_center=False,  # set input mean to 0 over the dataset
        samplewise_center=False,  # set each sample mean to 0
        featurewise_std_normalization=False,  # divide inputs by std of the dataset
        samplewise_std_normalization=False,  # divide each input by its std
        zca_whitening=False,  # apply ZCA whitening
        zca_epsilon=1e-06,  # epsilon for ZCA whitening
        rotation_range=0,  # randomly rotate images in the range (degrees, 0 to 180)
        # randomly shift images horizontally (fraction of total width)
        width_shift_range=0.1,
        # randomly shift images vertically (fraction of total height)
        height_shift_range=0.1,
        shear_range=0.,  # set range for random shear
        zoom_range=0.,  # set range for random zoom
        channel_shift_range=0.,  # set range for random channel shifts
        # set mode for filling points outside the input boundaries
        fill_mode='nearest',
        cval=0.,  # value used for fill_mode = "constant"
        horizontal_flip=True,  # randomly flip images
        vertical_flip=False,  # randomly flip images
        # set rescaling factor (applied before any other transformation)
        rescale=None,
        # set function that will be applied on each input
        preprocessing_function=None,
        # image data format, either "channels_first" or "channels_last"
        data_format=None,
        # fraction of images reserved for validation (strictly between 0 and 1)
        validation_split=0.0)

    # Compute quantities required for feature-wise normalization
    # (std, mean, and principal components if ZCA whitening is applied).
    datagen.fit(x_train)

    # Fit the model on the batches generated by datagen.flow().
    history = model.fit_generator(datagen.flow(x_train, y_train,
                                     batch_size=batch_size),
                        epochs=epochs,
                        validation_data=(x_test, y_test),
                        workers=4,
                        steps_per_epoch=x_train.shape[0]/batch_size)

# Save model and weights
if not os.path.isdir(save_dir):
    os.makedirs(save_dir)
model_path = os.path.join(save_dir, model_name)
model.save(model_path)
print('Saved trained model at %s ' % model_path)

# Score trained model.
scores = model.evaluate(x_test, y_test, verbose=1)
print('Test loss:', scores[0])
print('Test accuracy:', scores[1])


# Plot training & validation accuracy values
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Val'], loc='upper left')
plt.show()

# Plot training & validation loss values
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Val'], loc='upper left')
plt.show()
