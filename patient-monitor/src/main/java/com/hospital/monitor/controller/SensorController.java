package com.hospital.monitor.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.hospital.monitor.websocket.MonitorWebSocketHandler;
import com.hospital.monitor.entity.Patient;
import com.hospital.monitor.service.PatientService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/sensor")
@RequiredArgsConstructor
@Tag(name = "传感器管理", description = "传感器信号处理接口")
public class SensorController {

    private final PatientService patientService;
    private final MonitorWebSocketHandler monitorWebSocketHandler;
    private final ObjectMapper objectMapper;

    @PostMapping("/signal")
    @Operation(summary = "处理传感器信号")
    public Object handleSensorSignal(@RequestBody SensorRequest request) {
        Patient patient = patientService.handleSensorSignal(
                request.getPatientId(),
                request.getBehaviorType(),
                request.getDescription(),
                request.getIsAbnormal(),
                request.getSeverity()
        );

        if (Boolean.TRUE.equals(request.getIsAbnormal())) {
            try {
                String json = objectMapper.writeValueAsString(patient);
                monitorWebSocketHandler.broadcast(json);
            } catch (Exception e) {
                return "处理成功，但WebSocket推送失败: " + e.getMessage();
            }
        }

        return "处理成功";
    }

    public static class SensorRequest {
        private Long patientId;
        private String behaviorType;
        private String description;
        private Boolean isAbnormal;
        private Integer severity;

        public Long getPatientId() {
            return patientId;
        }

        public void setPatientId(Long patientId) {
            this.patientId = patientId;
        }

        public String getBehaviorType() {
            return behaviorType;
        }

        public void setBehaviorType(String behaviorType) {
            this.behaviorType = behaviorType;
        }

        public String getDescription() {
            return description;
        }

        public void setDescription(String description) {
            this.description = description;
        }

        public Boolean getIsAbnormal() {
            return isAbnormal;
        }

        public void setIsAbnormal(Boolean isAbnormal) {
            this.isAbnormal = isAbnormal;
        }

        public Integer getSeverity() {
            return severity;
        }

        public void setSeverity(Integer severity) {
            this.severity = severity;
        }
    }
}
