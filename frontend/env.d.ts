/// <reference types="vite/client" />

type ImportMetaEnv = {
  readonly VITE_TEXT_API_URL?: string;
  readonly VITE_URL_API_URL?: string;
  readonly VITE_IMAGE_API_URL?: string;
  readonly VITE_AUTH_API_URL?: string;
};

type ImportMeta = {
  readonly env: ImportMetaEnv;
};
