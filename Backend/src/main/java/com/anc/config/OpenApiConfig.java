package com.anc.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI neoSureOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("NeoSure - Maternal Health API")
                        .description("REST API for NeoSure Antenatal Care (ANC) Management System. " +
                                "This API provides endpoints for worker and doctor authentication, " +
                                "patient management, ANC visit registration with AI-powered risk assessment, " +
                                "and doctor consultations with video conferencing.")
                        .version("v1.0.0")
                        .contact(new Contact()
                                .name("NeoSure Team")
                                .email("support@neosure.health")
                                .url("https://neosure.health"))
                        .license(new License()
                                .name("MIT License")
                                .url("https://opensource.org/licenses/MIT")))
                .servers(List.of(
                        new Server()
                                .url("http://localhost:8080")
                                .description("Development Server"),
                        new Server()
                                .url("https://api.neosure.health")
                                .description("Production Server")))
                .addSecurityItem(new SecurityRequirement().addList("Bearer Authentication"))
                .components(new io.swagger.v3.oas.models.Components()
                        .addSecuritySchemes("Bearer Authentication",
                                new SecurityScheme()
                                        .type(SecurityScheme.Type.HTTP)
                                        .scheme("bearer")
                                        .bearerFormat("JWT")
                                        .description("Enter JWT token obtained from login endpoint")));
    }
}
