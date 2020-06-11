import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from tensorflow.keras import utils
from tensorflow.keras.preprocessing.image import load_img, img_to_array, array_to_img
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from tensorflow.keras.callbacks import EarlyStopping

# Here we need to set up our x and y
# y_train = utils.to_categorical(y_train)
# y_test = utils.to_categorical(y_test)

X = np.load('./main_tile_array_array.npy')
y = pd.read_csv('./diagnosis_df_saved.csv')

print('X Shape: ', X.shape())
print('Length of y: ', len(y))


y.drop(columns='diagnosis', inplace=True)

# y['Diagnosis'].value_counts(normalize=True)

# y = (y['Diagnosis'] == 'Mixed glioma').astype(int)
y['Diagnosis'] = y['Diagnosis'].map({'Oligodendroglioma, anaplastic' : 0,
           'Astrocytoma, anaplastic' : 1,
           'Mixed glioma' : 2,
           'Oligodendroglioma, NOS' : 3,
           'Astrocytoma, NOS' : 4
          })
# y = y.to_numpy()

y = [i for i in y['Diagnosis']]

y = np.array(y)

y = utils.to_categorical(y, 5)

X_model, X_holdout, y_model, y_holdout = train_test_split(X, y)

X_train, X_test, y_train, y_test = train_test_split(X_model, y_model)

# Make sure each value is a float. (Otherwise, we get an error.)
X_train = X_train.astype('float32')
X_test = X_test.astype('float32')
X_holdout = X_holdout.astype('float32')

# The current range of X_train and X_test is 0 to 255.
# The code below is equivalent to X_train = X_train / 255.
# This scales each value to be between 0 and 1.
X_train /= 255
X_test /= 255
X_holdout /= 255

cnn_model = Sequential()

cnn_model.add(Conv2D(
        filters = 6, # number of filters
        kernel_size = (3,3), # height/width of filter
        activation = 'relu',
        input_shape = (256, 256, 3)))


cnn_model.add(MaxPooling2D(pool_size=(2,2)))

cnn_model.add(Conv2D(32,
                     kernel_size=(3,3),
                     activation= 'relu'
                    ))

cnn_model.add(MaxPooling2D(pool_size=(2,2)))

cnn_model.add(Dropout(0.1))

# cnn_model.add(Conv2D(32,
#                      kernel_size=(3,3),
#                      activation= 'relu'
#                     ))

# cnn_model.add(MaxPooling2D(pool_size=(2,2)))

# cnn_model.add(Dropout(0.05))

cnn_model.add(Flatten())

cnn_model.add(Dense(128, activation='relu'))

cnn_model.add(Dense(5, activation='softmax'))

cnn_model.compile(loss='categorical_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])


early_stop = EarlyStopping(monitor='val_loss', min_delta=0, patience=20, verbose=1, mode='auto')


cnn_model.summary()
history = cnn_model.fit(X_train,
                        y_train,
                        batch_size=256,
                        validation_data=(X_test, y_test),
                        epochs=1000,
                        verbose=1,
                        callbacks = [early_stop])



# Check out our train loss and test loss over epochs.
train_loss = history.history['loss']
test_loss = history.history['val_loss']

# Set figure size.
plt.figure(figsize=(12, 8))

# Generate line plot of training, testing loss over epochs.
plt.plot(train_loss, label='Training Loss', color='#185fad')
plt.plot(test_loss, label='Testing Loss', color='orange')

# Set title
plt.title('Training and Testing Loss by Epoch', fontsize = 25)
plt.xlabel('Epoch', fontsize = 18)
plt.ylabel('Categorical Crossentropy', fontsize = 18)
plt.xticks(np.arange(10), np.arange(10))

plt.legend(fontsize = 18);
plt.savefig('./loss_graph.png',transparent = True)


from sklearn.metrics import confusion_matrix
save_confusion_matrix = confusion_matrix(y_holdout_true, ypreds)
np.save('./confustion_matrix.npy', save_confusion_matrix)
