{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "cla-backend.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "cla-backend.whitelist_additional" -}}
{{- if .Values.ingress.whitelist_additional -}}
,{{ join "," .Values.ingress.whitelist_additional }}
{{- end -}}
{{- end -}}

{{- define "cla-backend.whitelist" -}}
{{ join "," .Values.ingress.whitelist }},{{- .Values.pingdomIPs }}{{ include "cla-backend.whitelist_additional" . }}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "cla-backend.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "cla-backend.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Common labels
*/}}
{{- define "cla-backend.labels" -}}
helm.sh/chart: {{ include "cla-backend.chart" . }}
{{ include "cla-backend.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Selector labels
*/}}
{{- define "cla-backend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "cla-backend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/*
Create the name of the service account to use
*/}}
{{- define "cla-backend.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
    {{ default (include "cla-backend.fullname" .) .Values.serviceAccount.name }}
{{- else -}}
    {{ default "default" .Values.serviceAccount.name }}
{{- end -}}
{{- end -}}

{{/*
Local postgres env vars
*/}}
{{- define "cla-backend.localPostgresEnvVars" -}}
{{- if .Values.localPostgres.enabled }}
- name: DB_HOST
  value: {{ include "cla-backend.fullname" . }}-db
- name: DB_PORT
  value: "5432"
{{- end }}
{{- end -}}

{{- define "cla-backend.app.vars" -}}
{{- $environment := .Values.environment -}}
- name: ALLOWED_HOSTS
  value: "{{ .Values.host }}"
- name:  CLA_ENV
  value: "{{ $environment }}"
{{ range $name, $data := .Values.envVars }}
- name: {{ $name }}
{{- if $data.value }}
  value: "{{ $data.value }}"
{{- else if $data.secret }}
  valueFrom:
    secretKeyRef:
      name: {{ $data.secret.name }}
      key: {{ $data.secret.key }}
      {{- if eq $environment "development" }}
      optional: true
      {{- else }}
      optional: {{ $data.secret.optional | default false }}
      {{- end }}
{{- end -}}
{{- end -}}
{{ include "cla-backend.localPostgresEnvVars" . }}
{{- end -}}
