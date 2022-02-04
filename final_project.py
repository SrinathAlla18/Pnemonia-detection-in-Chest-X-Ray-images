# -*- coding: utf-8 -*-
"""final project

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zwy2zdBpFY3Yil-WraBT4Y6wJa8Y9Um-

# The link of the Dataset is the project final document(Dataset Section)
"""

import pandas as pd
import numpy as np
import tensorflow as tf
import os
import seaborn as sns
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense, Flatten
from keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import RMSprop,Adam,SGD
from sklearn.model_selection import train_test_split
from keras.applications.vgg16 import VGG16
#from keras.applications.ResNet50 import ResNet50
#from keras.applications import InceptionResNetV2
from keras.applications.vgg16 import preprocess_input
from sklearn.metrics import confusion_matrix, classification_report,accuracy_score,precision_score,recall_score

from google.colab import drive
drive.mount('/content/gdrive')

cd '/content/gdrive/My Drive/train/'

training_images = tf.io.gfile.glob('/content/gdrive/My Drive/train/*/*')
total_files = training_images
train_images, val_images = train_test_split(total_files, test_size = 0.1,random_state=42)
print(len(train_images))
print(len(val_images))

count_normal = len([x for x in train_images if "NORMAL" in x])
print(f'Normal images count in training set: {count_normal}')

count_pneumonia = len([x for x in train_images if "PNEUMONIA" in x])
print(f'Pneumonia images count in training set: {count_pneumonia}')

count_array = []
count_array += ['positive']*count_pneumonia
count_array += ['negative']*count_normal

sns.set_style('ticks')
sns.countplot(count_array)

tf.io.gfile.makedirs('/content/gdrive/My Drive/val_dataset/negative/')
tf.io.gfile.makedirs('/content/gdrive/My Drive/val_dataset/positive/')
tf.io.gfile.makedirs('/content/gdrive/My Drive/train_dataset/negative/')
tf.io.gfile.makedirs('/content/gdrive/My Drive/train_dataset/positive/')

train_datagen = ImageDataGenerator(rescale = 1/255,
                                 rotation_range = 30,
                                 zoom_range = 0.2,
                                 width_shift_range = 0.1,
                                 height_shift_range = 0.1)
val_datagen = ImageDataGenerator(rescale = 1/255)
                                

train_generator = train_datagen.flow_from_directory(
    '/content/gdrive/My Drive/train_dataset/',
    target_size = [300,300],
    class_mode = 'binary'
)

validation_generator = val_datagen.flow_from_directory(
    '/content/gdrive/My Drive/val_dataset/',
    target_size = [300,300],
    class_mode = 'binary')

eval_datagen = ImageDataGenerator(rescale = 1/255)

test_generator = eval_datagen.flow_from_directory(
    '/content/gdrive/My Drive/test',
    target_size =[300,300],
    class_mode = 'binary')

weight_for_0 = (1 / count_normal)*(len(train_images))/2.0 
weight_for_1 = (1 / count_pneumonia)*(len(train_images))/2.0

class_weight = {0: weight_for_0, 1: weight_for_1}

print('Weight for class 0: {:.2f}'.format(weight_for_0))
print('Weight for class 1: {:.2f}'.format(weight_for_1))

vgg=VGG16(input_shape=[300,300]+[3],weights='imagenet',include_top=False)
for layer in vgg.layers:
    layer.trainable=False

# INCEPTIONResNetV2
inception=InceptionResNetV2(input_shape=[150,150]+[3],weights='imagenet',include_top=False)
for layer in inception.layers:
    layer.trainable=False

model=Sequential([vgg,
                tf.keras.layers.Flatten(),
                tf.keras.layers.Dense(256, activation=tf.nn.relu),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Dense(256, activation=tf.nn.relu),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Dense(1,activation=tf.nn.sigmoid)])
model.compile(loss='binary_crossentropy',optimizer=RMSprop(lr=0.001),metrics=['accuracy',tf.keras.metrics.Precision(name='precision'),
        tf.keras.metrics.Recall(name='recall')])
model.summary()

checkpoint_cb1 = tf.keras.callbacks.ModelCheckpoint("model1_vgg.h5",save_best_only=True)

early_stopping_cb1 = tf.keras.callbacks.EarlyStopping(monitor ='val_loss', patience=20, mode = 'min',restore_best_weights=True)
history1 = model.fit(
    train_generator,
    steps_per_epoch = 64,
    epochs = 25,
    validation_data = validation_generator,
    class_weight = class_weight,
    callbacks = [early_stopping_cb1,checkpoint_cb1])

acc = history1.history['accuracy']
val_acc = history1.history['val_accuracy']

loss = history1.history['loss']
val_loss = history1.history['val_loss']

epochs_range = range(25)

plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()

eval_result1=model.evaluate_generator(test_generator)
print('loss rate on evaluation data :', eval_result1[0])
print('accuracy rate on evaluation data :', eval_result1[1])
print('precision on evaluation data :', eval_result1[2])
print('Recall on evaluation data :', eval_result1[3])

class_vgg=model.predict(test_generator)

for i in range (class_vgg.shape[0]):
  if class_vgg[i]<=0.5:
    class_vgg[i]==0
  else:
    class_vgg[i]==1

print(confusion_matrix(test_generator.classes, class_vgg))
pd.DataFrame(classification_report(test_generator.classes, class_vgg, output_dict=True))

"""#Model of InceptionResnetV2

"""



# Model for InceptionResnetV2
model_inception=Sequential([inception,
                tf.keras.layers.Flatten(), 
                tf.keras.layers.Dense(512,activation=tf.nn.relu),
                tf.keras.layers.Dropout(0.5),
                tf.keras.layers.Dense(512,activation=tf.nn.relu),
                tf.keras.layers.Dropout(0.7),
                tf.keras.layers.Dense(1,activation=tf.nn.sigmoid)])
model_inception.compile(loss='binary_crossentropy',optimizer=RMSprop(lr=0.001),metrics=['accuracy',tf.keras.metrics.Precision(name='precision'),
        tf.keras.metrics.Recall(name='recall')])
model_inception.summary()

checkpoint_cb1 = tf.keras.callbacks.ModelCheckpoint("model1_inception.h5",
                                                    save_best_only=True)
early_stopping_cb1 = tf.keras.callbacks.EarlyStopping(monitor ='val_loss', patience=10, mode = 'min',restore_best_weights=True)
history3 = model_inception.fit(
    train_generator,
    steps_per_epoch = 10,
    epochs = 20,
    validation_data = validation_generator,
    class_weight=class_weight)

eval_result1=model_inception.evaluate(test_generator)
print('loss rate on evaluation data :', eval_result1[0])
print('accuracy rate on evaluation data :', eval_result1[1])
print('Precision on evaluation data :', eval_result1[2])
print('Recall on evaluation data :', eval_result1[3])

class_inception=model_inception.predict_classes(test_generator)

print(confusion_matrix(test_generator.classes,class_inception))
pd.DataFrame(classification_report(test_generator.classes,class_inception, output_dict=True))

acc = history3.history['accuracy']
val_acc = history3.history['val_accuracy']

loss = history3.history['loss']
val_loss = history3.history['val_loss']

epochs_range = range(20)

plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()

"""#Model of INCEPTION V3"""

# Inception v3 model
from keras.applications.inception_v3 import InceptionV3
# create the base pre-trained model
base_model = InceptionV3(weights=None, include_top=False,input_shape=(150, 150,3) )

train_datagen = ImageDataGenerator(rescale=1/ 255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True)
val_datagen = ImageDataGenerator(rescale = 1/255)
                                

train_generator = train_datagen.flow_from_directory(
    '/content/gdrive/My Drive/train_dataset/',
    target_size = [150,150],
    class_mode = 'binary'
)

validation_generator = val_datagen.flow_from_directory(
    '/content/gdrive/My Drive/val_dataset/',
    target_size = [150,150],
    class_mode = 'binary')
eval_datagen = ImageDataGenerator(rescale = 1/255)

test_generator = eval_datagen.flow_from_directory(
    '/content/gdrive/My Drive/test',
    target_size =[150,150],
    class_mode = 'binary')

# Model for inception v2
model_v2=Sequential([base_model,
                tf.keras.layers.Dropout(0.5),                    
                tf.keras.layers.GlobalAveragePooling2D(),
                tf.keras.layers.Dense(128, activation='relu'),
                tf.keras.layers.BatchNormalization(),
                tf.keras.layers.Dense(1, activation='sigmoid')])
model_v2.compile(loss='binary_crossentropy',optimizer='Adam',metrics=['accuracy',tf.keras.metrics.Precision(name='precision'),
        tf.keras.metrics.Recall(name='recall')])
model_v2.summary()

from keras.callbacks import ReduceLROnPlateau , ModelCheckpoint , LearningRateScheduler
lr_reduce = ReduceLROnPlateau(monitor='val_accuracy', factor=0.1, epsilon=0.0001, patience=1, verbose=1)
checkpoint= tf.keras.callbacks.ModelCheckpoint("model_v2.h5",
                                                    save_best_only=True)

history = model_v2.fit(train_generator, validation_data = validation_generator ,callbacks=[lr_reduce,checkpoint] ,
          epochs=15)

eval_result1=model_v2.evaluate_generator(test_generator)
print('loss rate on evaluation data :', eval_result1[0])
print('accuracy rate on evaluation data :', eval_result1[1])
print('precision on evaluation data :', eval_result1[2])
print('recall on evaluation data :', eval_result1[1])

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(15)

plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()

class_v2=model_v2.predict_classes(test_generator)

print(confusion_matrix(test_generator.classes,class_v2))

"""#Ensemble by majority """

|# Ensemble of VGG16, inceptionresentv2 and  inceptionv3
class_Ensemble=[]
for i in range(len(class_v2)):
  l=[]
  l.append(class_v2[i][0])
  l.append(class_inception[i][0])
  l.append(class_vgg[i][0])
  class_Ensemble.append(l)

final=[]
for i in range (len(class_Ensemble)):
  output=[]
  class_Ensemble[i].sort()
  output.append(class_Ensemble[i][1])
  final.append(output)

print(confusion_matrix(test_generator.classes,final))
pd.DataFrame(classification_report(test_generator.classes,final, output_dict=True))

