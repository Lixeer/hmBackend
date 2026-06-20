package com.hospital.monitor;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.hospital.monitor.mapper")
public class PatientMonitorApplication {

    public static void main(String[] args) {
        SpringApplication.run(PatientMonitorApplication.class, args);
    }
}
