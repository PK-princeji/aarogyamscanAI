
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import DenseNet121
from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

def get_base_model(img_size):
    # DenseNet121 सबसे बेस्ट है मेडिकल के लिए
    base = DenseNet121(weights='imagenet', include_top=False, input_shape=(img_size, img_size, 3))
    base.trainable = False
    return base

def build_disease_model(num_classes, img_size=224):
    base_model = get_base_model(img_size)
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.BatchNormalization(),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.4),
        layers.Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer=optimizers.Adam(1e-4), loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def train_engine(data_dir, model_save_path, img_size=224, epochs=10):
    # यह फंक्शन किसी भी बीमारी के लिए काम करेगा
    datagen = ImageDataGenerator(
        rescale=1./255, validation_split=0.2,
        rotation_range=15, zoom_range=0.2, horizontal_flip=True
    )
    
    train_gen = datagen.flow_from_directory(
        data_dir, target_size=(img_size, img_size), batch_size=16, 
        class_mode='categorical', subset='training'
    )
    
    val_gen = datagen.flow_from_directory(
        data_dir, target_size=(img_size, img_size), batch_size=16, 
        class_mode='categorical', subset='validation'
    )
    
    model = build_disease_model(len(train_gen.class_indices), img_size)
    
    checkpoint = ModelCheckpoint(model_save_path, save_best_only=True, monitor='val_accuracy')
    model.fit(train_gen, epochs=epochs, validation_data=val_gen, callbacks=[checkpoint])
    print(f"✅ Model Saved: {model_save_path}")
