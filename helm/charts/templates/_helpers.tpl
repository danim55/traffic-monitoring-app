{{/*
  Renders the Docker configuration JSON (base64‑encoded) for pulling images
  from a registry.

  Required Values:
    .Values.image.registry
    .Values.image.pullSecret.username
    .Values.image.pullSecret.password
*/}}
{{- define "detector.imagePullDockerConfigJson" -}}
{{- $registry := required "Registry address is required" .Values.image.registry }}
{{- $username := required "Username is required" .Values.image.pullSecret.username }}
{{- $password := required "Password is required" .Values.image.pullSecret.password }}
{{- printf "{\"auths\":{\"%s\":{\"username\":\"%s\",\"password\":\"%s\"}}}" $registry $username $password | b64enc }}
{{- end -}}
