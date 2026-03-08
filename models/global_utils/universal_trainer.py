
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import DenseNet121
from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from tensorflow.keras.applications.densenet import preprocess_input

def train_engine(data_dir, save_path, img_size=224, epochs=15, batch_size=16):
    print(f"🚀 Universal Trainer Started for: {save_path}")
    
    # Data Augmentation (मॉडल को रटने से रोकने के लिए)
    train_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input, # DenseNet Special
        validation_split=0.2,      # 20% डेटा टेस्टिंग के लिए
        rotation_range=15,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )

    print("⏳ Loading Training Data...")
    try:
        train_generator = train_datagen.flow_from_directory(
            data_dir, target_size=(img_size, img_size), 
            batch_size=batch_size, class_mode='categorical', subset='training'
        )

        print("⏳ Loading Validation Data...")
        val_generator = train_datagen.flow_from_directory(
            data_dir, target_size=(img_size, img_size), 
            batch_size=batch_size, class_mode='categorical', subset='validation'
        )
    except:
        print("❌ Error: डेटा नहीं मिला! कृपया dataset फोल्डर में इमेज डालें।")
        return

    # क्लास चेक
    num_classes = len(train_generator.class_indices)
    print(f"🏷️ Classes Found: {train_generator.class_indices}")

    # Transfer Learning Model (DenseNet121)
    base_model = DenseNet121(weights='imagenet', include_top=False, input_shape=(img_size, img_size, 3))
    base_model.trainable = False # बेस को फ्रीज़ करें

    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.BatchNormalization(),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.4),
        layers.Dense(num_classes, activation='softmax') # Softmax for multi-class
    ])

    model.compile(optimizer=optimizers.Adam(learning_rate=0.0001), 
                  loss='categorical_crossentropy', metrics=['accuracy'])

    # ट्रेनिंग शुरू
    checkpoint = ModelCheckpoint(save_path, save_best_only=True, monitor='val_accuracy', verbose=1)
    early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

    print("🔥 Training Running...")
    model.fit(train_generator, epochs=epochs, validation_data=val_generator, callbacks=[checkpoint, early_stop])
    print(f"✅ FINAL MODEL SAVED: {save_path}")
