package com.hospital.monitor.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;

public class SeverityUpdateRequest {

    @NotNull(message = "异常等级不能为空")
    @Min(value = 0, message = "异常等级最小为0")
    @Max(value = 5, message = "异常等级最大为5")
    private Integer severity;

    public Integer getSeverity() {
        return severity;
    }

    public void setSeverity(Integer severity) {
        this.severity = severity;
    }
}