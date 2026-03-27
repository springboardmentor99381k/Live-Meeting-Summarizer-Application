import os


def _load_dotenv_from_project_root() -> None:
	"""Load key=value pairs from project .env into process env if unset."""
	config_dir = os.path.dirname(__file__)
	package_dir = os.path.dirname(config_dir)
	project_root = os.path.dirname(package_dir)
	env_path = os.path.join(project_root, ".env")

	if not os.path.isfile(env_path):
		return

	try:
		with open(env_path, "r", encoding="utf-8") as env_file:
			for raw_line in env_file:
				line = raw_line.strip()
				if not line or line.startswith("#") or "=" not in line:
					continue

				key, value = line.split("=", 1)
				key = key.strip()
				value = value.strip().strip('"').strip("'")

				# Keep explicit process env values higher priority.
				if key and key not in os.environ:
					os.environ[key] = value
	except OSError:
		# If .env cannot be read, continue with normal env lookups.
		pass


def _as_int(name: str, default: int) -> int:
	raw = os.getenv(name)
	if raw is None:
		return default
	try:
		return int(raw)
	except ValueError:
		return default


def _as_csv(name: str) -> list[str]:
	raw = os.getenv(name, "")
	return [item.strip() for item in raw.split(",") if item.strip()]


def _as_csv_many(*names: str) -> list[str]:
	values: list[str] = []
	seen: set[str] = set()

	for name in names:
		for item in _as_csv(name):
			if item not in seen:
				seen.add(item)
				values.append(item)

	return values


_load_dotenv_from_project_root()

AUDIO_SAMPLE_RATE = _as_int("AUDIO_SAMPLE_RATE", 16000)
AUDIO_CHANNELS = _as_int("AUDIO_CHANNELS", 1)
AUDIO_CHUNK_SIZE = _as_int("AUDIO_CHUNK_SIZE", 1024)

WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

OUTPUTS_DIR = os.getenv("OUTPUTS_DIR", "outputs")
TEMP_DIR = os.getenv("TEMP_DIR", "temp")
CORS_ALLOWED_ORIGINS = _as_csv_many("CORS_ALLOWED_ORIGINS", "ALLOWED_ORIGINS")
