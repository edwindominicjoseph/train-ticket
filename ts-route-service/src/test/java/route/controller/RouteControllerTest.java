package route.controller;

import com.alibaba.fastjson.JSONObject;
import edu.fudan.common.util.Response;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.web.client.RestTemplateAutoConfiguration;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.http.*;
import org.springframework.test.context.junit4.SpringRunner;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import org.springframework.test.web.servlet.result.MockMvcResultMatchers;
import route.config.SecurityConfig;
import route.entity.RouteInfo;
import route.service.RouteService;

import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Base64;
import java.util.Date;

@RunWith(SpringRunner.class)
@WebMvcTest(RouteController.class)
@Import({SecurityConfig.class, RestTemplateAutoConfiguration.class})
public class RouteControllerTest {

    @MockBean
    private RouteService routeService;

    @Autowired
    private MockMvc mockMvc;

    private Response response = new Response();

    @Test
    public void testHome() throws Exception {
        mockMvc.perform(MockMvcRequestBuilders.get("/api/v1/routeservice/welcome"))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andExpect(MockMvcResultMatchers.content().string("Welcome to [ Route Service ] !"));
    }

    @Test
    public void testCreateAndModifyRoute() throws Exception {
        RouteInfo createAndModifyRouteInfo = new RouteInfo();
        Mockito.when(routeService.createAndModify(Mockito.any(RouteInfo.class), Mockito.any(HttpHeaders.class))).thenReturn(response);
        String requestJson = JSONObject.toJSONString(createAndModifyRouteInfo);
        String result = mockMvc.perform(MockMvcRequestBuilders.post("/api/v1/routeservice/routes")
                .header(HttpHeaders.AUTHORIZATION, adminAuthorization())
                .contentType(MediaType.APPLICATION_JSON).content(requestJson))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andReturn().getResponse().getContentAsString();
        Assert.assertEquals(response, JSONObject.parseObject(result, Response.class));
    }

    @Test
    public void testDeleteRoute() throws Exception {
        Mockito.when(routeService.deleteRoute(Mockito.anyString(), Mockito.any(HttpHeaders.class))).thenReturn(response);
        String result = mockMvc.perform(MockMvcRequestBuilders.delete("/api/v1/routeservice/routes/route_id")
                .header(HttpHeaders.AUTHORIZATION, adminAuthorization()))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andReturn().getResponse().getContentAsString();
        Assert.assertEquals(response, JSONObject.parseObject(result, Response.class));
    }

    @Test
    public void testQueryById() throws Exception {
        Mockito.when(routeService.getRouteById(Mockito.anyString(), Mockito.any(HttpHeaders.class))).thenReturn(response);
        String result = mockMvc.perform(MockMvcRequestBuilders.get("/api/v1/routeservice/routes/route_id"))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andReturn().getResponse().getContentAsString();
        Assert.assertEquals(response, JSONObject.parseObject(result, Response.class));
    }

    @Test
    public void testQueryAll() throws Exception {
        Mockito.when(routeService.getAllRoutes(Mockito.any(HttpHeaders.class))).thenReturn(response);
        String result = mockMvc.perform(MockMvcRequestBuilders.get("/api/v1/routeservice/routes"))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andReturn().getResponse().getContentAsString();
        Assert.assertEquals(response, JSONObject.parseObject(result, Response.class));
    }

    @Test
    public void testQueryByStartAndTerminal() throws Exception {
        Mockito.when(routeService.getRouteByStartAndEnd(Mockito.anyString(), Mockito.anyString(), Mockito.any(HttpHeaders.class))).thenReturn(response);
        String result = mockMvc.perform(MockMvcRequestBuilders.get("/api/v1/routeservice/routes/start_id/terminal_id"))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andReturn().getResponse().getContentAsString();
        Assert.assertEquals(response, JSONObject.parseObject(result, Response.class));
    }

    @Test
    public void anonymousCreateIsForbidden() throws Exception {
        mockMvc.perform(MockMvcRequestBuilders.post("/api/v1/routeservice/routes")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{}"))
                .andExpect(MockMvcResultMatchers.status().isForbidden());
    }

    @Test
    public void anonymousDeleteIsForbidden() throws Exception {
        mockMvc.perform(MockMvcRequestBuilders.delete("/api/v1/routeservice/routes/route_id"))
                .andExpect(MockMvcResultMatchers.status().isForbidden());
    }

    private String adminAuthorization() {
        String rawSecret = System.getenv("JWT_SECRET");
        if (rawSecret == null || rawSecret.length() < 32) {
            throw new IllegalStateException("JWT_SECRET must contain at least 32 characters for security tests");
        }
        String signingKey = Base64.getEncoder().encodeToString(rawSecret.getBytes(StandardCharsets.UTF_8));
        String token = Jwts.builder()
                .setSubject("route-test-admin")
                .claim("roles", Arrays.asList("ROLE_ADMIN"))
                .setIssuedAt(new Date())
                .setExpiration(new Date(System.currentTimeMillis() + 60000))
                .signWith(SignatureAlgorithm.HS256, signingKey)
                .compact();
        return "Bearer " + token;
    }

}
