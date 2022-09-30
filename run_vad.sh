# activate virtual environment
source .venv/bin/activate

# since WSL requires PulseAudio, I need to set up that first
export PULSE_SERVER=tcp:localhost

# run coqui STT
python3 -u coqui_vad.py -m /mnt/e/ML/coqui-stt-0.9.3-models.pbmm -s /mnt/e/ML/coqui-stt-0.9.3-models.scorer

# echo "Hello from SHELL!"