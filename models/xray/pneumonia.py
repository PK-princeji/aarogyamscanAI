# Chest X-Ray AI Training Script with Detailed Logs and Epoch Time Info
# pneumonia.py
import os
import psutil
import pandas as pd
import tensorflow as tf
from datetime import datetime
from tensorflow.keras import layers, Model
from tensorflow.keras.applications import DenseNet121
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau

# ----------------- CONFIG -----------------
BASE = r"D:/final_year_project/code_X_Elite/aarogyamScanAi"
DATA_DIR = os.path.join(BASE, "dataset")

IMAGE_FOLDERS = [f"images_{str(i).zfill(3)}" for i in range(1, 13)]
CSV_FILE = os.path.join(DATA_DIR, "Data_Entry_2017.csv")
TRAIN_LIST = os.path.join(DATA_DIR, "train_val_list.txt")
TEST_LIST = os.path.join(DATA_DIR, "test_list.txt")

MODEL_DIR = os.path.join(BASE, "models", "xray")
os.makedirs(MODEL_DIR, exist_ok=True)

IMG_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS = 15
NUM_CLASSES = 2

# ----------------- UTILITY -----------------
def log_sys_status(step=""):
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    print(f"🖥️ [{step}] CPU Usage: {cpu:.1f}% | Memory Usage: {mem:.1f}%")

def make_df():
    print("🔄 Loading dataset metadata...")
    log_sys_status("Loading CSV")
    df = pd.read_csv(CSV_FILE)[['Image Index', 'Finding Labels']]
    df.columns = ['Image', 'Finding']
    df['label'] = df['Finding'].str.contains('Pneumonia', case=False, na=False).astype(int)

    image_base_paths = [os.path.join(DATA_DIR, folder) for folder in IMAGE_FOLDERS]
    def find_image_path(img_name):
        for base_path in image_base_paths:
            p = os.path.join(base_path, img_name)
            if os.path.exists(p):
                return p
        for base_path in image_base_paths:
            for root, dirs, files in os.walk(base_path):
                if img_name in files:
                    return os.path.join(root, img_name)
        return None

    print(f"🔍 Searching in {len(IMAGE_FOLDERS)} folders...")
    df['path'] = df['Image'].apply(find_image_path)

    initial_count = len(df)
    df = df.dropna(subset=['path']).reset_index(drop=True)
    found_count = len(df)
    pneumonia_count = df['label'].sum()
    normal_count = len(df) - pneumonia_count

    print(f"📊 Dataset Summary:")
    print(f"   Total images: {initial_count:,} | Found: {found_count:,}")
    print(f"   Normal: {normal_count:,} | Pneumonia: {pneumonia_count:,}")
    log_sys_status("Dataset Prepared")
    return df

def read_list(file_path):
    log_sys_status(f"Reading {file_path}")
    with open(file_path, 'r') as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    return set([os.path.basename(l) for l in lines])

def build_datasets(df):
    print("🔀 Splitting datasets...")
    log_sys_status("Splitting")
    train_set_names = read_list(TRAIN_LIST)
    test_set_names = read_list(TEST_LIST)

    df['basename'] = df['Image'].apply(lambda x: os.path.basename(x))
    train_df = df[df['basename'].isin(train_set_names)].reset_index(drop=True)
    test_df = df[df['basename'].isin(test_set_names)].reset_index(drop=True)
    val_df = train_df.sample(frac=0.1, random_state=42)
    train_df = train_df.drop(val_df.index).reset_index(drop=True)
    val_df = val_df.reset_index(drop=True)

    print(f"📈 Dataset Split:")
    print(f"   Train: {len(train_df)} | Val: {len(val_df)} | Test: {len(test_df)}")
    log_sys_status("Datasets Ready")
    return train_df, val_df, test_df

def preprocess_image(path, label):
    img = tf.io.read_file(path)
    img = tf.io.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, IMG_SIZE)
    img = img / 255.0
    return img, label

def df_to_dataset(df, shuffle=True):
    print(f"🗂️ Creating dataset (shuffle={shuffle}) with {len(df)} samples...")
    log_sys_status("Dataset Batching")
    paths = df['path'].values
    labels = df['label'].values
    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    ds = ds.map(lambda p, l: preprocess_image(p, l), num_parallel_calls=tf.data.AUTOTUNE)
    if shuffle:
        ds = ds.shuffle(1024)
    ds = ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    return ds

def build_model():
    print("🏗️ Building DenseNet121 model...")
    log_sys_status("Building Model")
    base = DenseNet121(include_top=False, weights='imagenet', input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3))
    base.trainable = False
    x = layers.GlobalAveragePooling2D()(base.output)
    x = layers.Dropout(0.4)(x)
    x = layers.Dense(256, activation='relu')(x)
    out = layers.Dense(1, activation='sigmoid')(x)
    model = Model(inputs=base.input, outputs=out, name='AarogyamScanAI_Xray')
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()])
    log_sys_status("Model Compiled")
    return model

# ----------------- EPOCH TIME LOGGER -----------------
class EpochTimeLogger(tf.keras.callbacks.Callback):
    def on_train_begin(self, logs=None):
        self.train_start_time = datetime.now()

    def on_epoch_begin(self, epoch, logs=None):
        self.epoch_start_time = datetime.now()
        print(f"\n⏳ Starting Epoch {epoch+1}...")

    def on_epoch_end(self, epoch, logs=None):
        epoch_end_time = datetime.now()
        elapsed = (epoch_end_time - self.epoch_start_time).total_seconds()
        total_elapsed = (epoch_end_time - self.train_start_time).total_seconds()
        epochs_done = epoch + 1
        total_epochs = self.params['epochs']
        remaining_epochs = total_epochs - epochs_done
        est_remaining = remaining_epochs * elapsed
        print(f"✅ Epoch {epoch+1} completed in {elapsed:.1f}s")
        print(f"🕒 Total elapsed: {total_elapsed/60:.1f} min | Estimated remaining: {est_remaining/60:.1f} min")
        progress = (epochs_done/total_epochs)*100
        print(f"📊 Progress: {progress:.1f}%\n")

# ----------------- MAIN FUNCTION -----------------
def main():
    print("🚀 AarogyamScanAI - Chest X-Ray Pneumonia Detection")
    print("="*60)
    print(f"📅 Training Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💾 Model Directory: {MODEL_DIR}")
    print("="*60)

    df = make_df()
    train_df, val_df, test_df = build_datasets(df)
    train_ds = df_to_dataset(train_df, shuffle=True)
    val_ds = df_to_dataset(val_df, shuffle=False)
    test_ds = df_to_dataset(test_df, shuffle=False)

    model = build_model()
    print("\n📋 Model Architecture:")
    model.summary()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    best_model_path = os.path.join(MODEL_DIR, f"AarogyamScanAI_xray_best_{timestamp}.h5")
    final_model_path = os.path.join(MODEL_DIR, f"AarogyamScanAI_xray_final_{timestamp}.h5")

    ckpt = ModelCheckpoint(best_model_path, monitor='val_accuracy', save_best_only=True, verbose=1, mode='max')
    es = EarlyStopping(monitor='val_accuracy', patience=5, restore_best_weights=True, verbose=1)
    rl = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=1, min_lr=1e-7)
    time_logger = EpochTimeLogger()

    print(f"\n🎯 Training for {EPOCHS} epochs...")
    log_sys_status("Before Training")
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS,
        callbacks=[ckpt, es, rl, time_logger],
        verbose=1
    )
    log_sys_status("After Training")

    print(f"\n📊 Evaluating on Test Set...")
    test_results = model.evaluate(test_ds, verbose=1)
    test_loss, test_acc, test_precision, test_recall = test_results
    f1_score = 2*(test_precision*test_recall)/(test_precision+test_recall) if (test_precision+test_recall)>0 else 0

    print(f"✅ Test Results:")
    print(f"   Accuracy: {test_acc*100:.2f}%")
    print(f"   Precision: {test_precision*100:.2f}%")
    print(f"   Recall: {test_recall*100:.2f}%")
    print(f"   F1-Score: {f1_score*100:.2f}%")
    log_sys_status("Evaluation Done")

    model.save(final_model_path)
    print(f"\n🎉 Training Completed Successfully! Models saved.")
    log_sys_status("End")

if __name__ == "__main__":
    main()
