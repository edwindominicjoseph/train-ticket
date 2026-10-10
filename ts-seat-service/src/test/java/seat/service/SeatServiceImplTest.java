package seat.service;

import edu.fudan.common.util.Response;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.MockitoAnnotations;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.*;
import org.springframework.web.client.RestTemplate;
import edu.fudan.common.entity.*;

import java.util.Arrays;

@RunWith(JUnit4.class)
public class SeatServiceImplTest {

    @InjectMocks
    private SeatServiceImpl seatServiceImpl;

    @Mock
    private RestTemplate restTemplate;

    private HttpHeaders headers = new HttpHeaders();

    @Before
    public void setUp() {
        MockitoAnnotations.initMocks(this);
    }

    @Test
    public void testDistributeSeat1() {
        Seat seat = new Seat();
        seat.setTrainNumber("G");
        seat.setSeatType(2);
        seat.setStartStation("start_station");
        seat.setDestStation("dest_station");
        seat.setTotalNum(100);
        seat.setStations(Arrays.asList("start_station", "dest_station"));

        Response<LeftTicketInfo> response2 = new Response<>();
        ResponseEntity<Response<LeftTicketInfo>> re2 = new ResponseEntity<>(response2, HttpStatus.OK);

        Mockito.when(restTemplate.exchange(
                Mockito.anyString(),
                Mockito.any(HttpMethod.class),
                Mockito.any(HttpEntity.class),
                Mockito.any(ParameterizedTypeReference.class)))
                .thenReturn(re2);

        Response result = seatServiceImpl.distributeSeat(seat, headers);
        Assert.assertEquals("Use a new seat number!", result.getMsg());
    }

    @Test
    public void testDistributeSeat2() {
        Seat seat = new Seat();
        seat.setTrainNumber("K");
        seat.setSeatType(3);
        seat.setStartStation("start_station");
        seat.setDestStation("dest_station");
        seat.setTotalNum(100);
        seat.setStations(Arrays.asList("start_station", "dest_station"));

        Response<LeftTicketInfo> response2 = new Response<>();
        ResponseEntity<Response<LeftTicketInfo>> re2 = new ResponseEntity<>(response2, HttpStatus.OK);

        Mockito.when(restTemplate.exchange(
                Mockito.anyString(),
                Mockito.any(HttpMethod.class),
                Mockito.any(HttpEntity.class),
                Mockito.any(ParameterizedTypeReference.class)))
                .thenReturn(re2);

        Response result = seatServiceImpl.distributeSeat(seat, headers);
        Assert.assertEquals("Use a new seat number!", result.getMsg());
    }

    @Test
    public void testGetLeftTicketOfInterval() {
        Seat seat = new Seat();
        seat.setTrainNumber("G");
        seat.setSeatType(2);
        seat.setStartStation("start_station");
        seat.setDestStation("dest_station");
        seat.setTotalNum(100);
        seat.setStations(Arrays.asList("start_station", "dest_station"));

        Response<LeftTicketInfo> response2 = new Response<>();
        ResponseEntity<Response<LeftTicketInfo>> re2 = new ResponseEntity<>(response2, HttpStatus.OK);

        Config config = new Config();
        config.setValue("0");
        Response<Config> response4 = new Response<>(null, null, config);
        ResponseEntity<Response<Config>> re4 = new ResponseEntity<>(response4, HttpStatus.OK);

        Mockito.when(restTemplate.exchange(
                Mockito.anyString(),
                Mockito.any(HttpMethod.class),
                Mockito.any(HttpEntity.class),
                Mockito.any(ParameterizedTypeReference.class)))
                .thenReturn(re2).thenReturn(re4);

        Response result = seatServiceImpl.getLeftTicketOfInterval(seat, headers);
        Assert.assertEquals(new Response<>(1, "Get Left Ticket of Internal Success", 0), result);
    }

    @Test
    public void testGetLeftTicketOfInterva2() {
        Seat seat = new Seat();
        seat.setTrainNumber("K");
        seat.setSeatType(3);
        seat.setStartStation("start_station");
        seat.setDestStation("dest_station");
        seat.setTotalNum(100);
        seat.setStations(Arrays.asList("start_station", "dest_station"));

        Response<LeftTicketInfo> response2 = new Response<>();
        ResponseEntity<Response<LeftTicketInfo>> re2 = new ResponseEntity<>(response2, HttpStatus.OK);

        Config config = new Config();
        config.setValue("0");
        Response<Config> response4 = new Response<>(null, null, config);
        ResponseEntity<Response<Config>> re4 = new ResponseEntity<>(response4, HttpStatus.OK);

        Mockito.when(restTemplate.exchange(
                Mockito.anyString(),
                Mockito.any(HttpMethod.class),
                Mockito.any(HttpEntity.class),
                Mockito.any(ParameterizedTypeReference.class)))
                .thenReturn(re2).thenReturn(re4);

        Response result = seatServiceImpl.getLeftTicketOfInterval(seat, headers);
        Assert.assertEquals(new Response<>(1, "Get Left Ticket of Internal Success", 0), result);
    }
}
