{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "..name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "..fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "..chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
UI labels
*/}}
{{- define "..uiLabels" -}}
{{- include "..labels" . }}
app.kubernetes.io/component: ui
{{- end }}

{{/*
UI selector labels
*/}}
{{- define "..uiSelectorLabels" -}}
{{- include "..selectorLabels" . }}
app.kubernetes.io/component: ui
{{- end }}

{{/*
Server labels
*/}}
{{- define "..serverLabels" -}}
{{- include "..labels" . }}
app.kubernetes.io/component: server
{{- end }}

{{/*
Server selector labels
*/}}
{{- define "..serverSelectorLabels" -}}
{{- include "..selectorLabels" . }}
app.kubernetes.io/component: server
{{- end }}

{{/*
Common labels
*/}}
{{- define "..labels" -}}
helm.sh/chart: {{ include "..chart" . }}
{{ include "..selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "..selectorLabels" -}}
app.kubernetes.io/name: {{ include "..name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "..serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "..fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Server Env
*/}}
{{- define "..serverEnv" -}}
- name: SECRET_KEY
  valueFrom:
    secretKeyRef:
      name: server-secrets
      key: secret-key
- name: POSTGRES_PASSWORD
  valueFrom:
    secretKeyRef:
      name: server-secrets
      key: db-password
{{- if .Values.DEV }}
- name: DB_HOSTNAME
  value: 'postgresql-headless'
- name: DEBUG
  value: 'true'
{{- end }}
{{- end }}
