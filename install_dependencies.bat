@echo off
echo Installing LogSec 3.0 Enhanced Dependencies...
echo.
echo [1/6] Installing Sentence Transformers for embeddings...
pip install sentence-transformers

echo.
echo [2/6] Installing FAISS for vector search...
pip install faiss-cpu

echo.
echo [3/6] Installing scikit-learn for clustering...
pip install scikit-learn

echo.
echo [4/6] Installing numpy for numerical operations...
pip install numpy

echo.
echo [5/6] Installing langdetect for multi-language support...
pip install langdetect

echo.
echo [6/6] Installing torch (required by sentence-transformers)...
pip install torch

echo.
echo ========================================
echo Installation complete!
echo.
echo Optional (for full ML features):
echo pip install tensorflow
echo pip install pandas
echo pip install matplotlib
echo.
pause
