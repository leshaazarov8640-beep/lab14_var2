package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"
)

type WeatherData struct {
	City        string    `json:"city"`
	Temp        float64   `json:"temp"`
	FeelsLike   float64   `json:"feels_like"`
	Humidity    int       `json:"humidity"`
	Pressure    int       `json:"pressure"`
	WindSpeed   float64   `json:"wind_speed"`
	WeatherDesc string    `json:"weather_desc"`
	Timestamp   time.Time `json:"timestamp"`
}

type WeatherResponse struct {
	Main struct {
		Temp      float64 `json:"temp"`
		FeelsLike float64 `json:"feels_like"`
		Humidity  int     `json:"humidity"`
		Pressure  int     `json:"pressure"`
	} `json:"main"`
	Wind struct {
		Speed float64 `json:"speed"`
	} `json:"wind"`
	Weather []struct {
		Description string `json:"description"`
	} `json:"weather"`
}

var cities = []string{
	"Moscow", "London", "New York", "Tokyo", "Paris",
	"Berlin", "Sydney", "Dubai", "Singapore", "Toronto",
}

func fetchWeather(city string, apiKey string) (*WeatherData, error) {
	url := fmt.Sprintf("https://api.openweathermap.org/data/2.5/weather?q=%s&appid=%s&units=metric", city, apiKey)

	resp, err := http.Get(url)
	if err != nil {
		return nil, fmt.Errorf("http get %s: %w", city, err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("read body %s: %w", city, err)
	}

	var wr WeatherResponse
	if err := json.Unmarshal(body, &wr); err != nil {
		return nil, fmt.Errorf("unmarshal %s: %w", city, err)
	}

	weatherDesc := ""
	if len(wr.Weather) > 0 {
		weatherDesc = wr.Weather[0].Description
	}

	return &WeatherData{
		City:        city,
		Temp:        wr.Main.Temp,
		FeelsLike:   wr.Main.FeelsLike,
		Humidity:    wr.Main.Humidity,
		Pressure:    wr.Main.Pressure,
		WindSpeed:   wr.Wind.Speed,
		WeatherDesc: weatherDesc,
		Timestamp:   time.Now(),
	}, nil
}

func collectWeather(apiKey string, interval time.Duration) <-chan WeatherData {
	ch := make(chan WeatherData, 100)
	var wg sync.WaitGroup

	go func() {
		ticker := time.NewTicker(interval)
		defer ticker.Stop()

		sigCh := make(chan os.Signal, 1)
		signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)

		for {
			select {
			case <-ticker.C:
				for _, city := range cities {
					wg.Add(1)
					go func(c string) {
						defer wg.Done()
						data, err := fetchWeather(c, apiKey)
						if err != nil {
							log.Printf("Error fetching %s: %v", c, err)
							return
						}
						ch <- *data
					}(city)
				}
			case <-sigCh:
				log.Println("Shutting down collector...")
				wg.Wait()
				close(ch)
				return
			}
		}
	}()

	return ch
}

func batchWriter(ch <-chan WeatherData, batchSize int, maxWait time.Duration) {
	file, err := os.OpenFile("weather_data.json", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatalf("Failed to open file: %v", err)
	}
	defer file.Close()

	buffer := make([]WeatherData, 0, batchSize)
	timer := time.NewTimer(maxWait)
	timer.Stop()

	for {
		select {
		case data, ok := <-ch:
			if !ok {
				flushBuffer(file, buffer)
				return
			}
			buffer = append(buffer, data)
			if len(buffer) >= batchSize {
				flushBuffer(file, buffer)
				buffer = buffer[:0]
				timer.Stop()
			} else if len(buffer) == 1 {
				timer.Reset(maxWait)
			}
		case <-timer.C:
			if len(buffer) > 0 {
				flushBuffer(file, buffer)
				buffer = buffer[:0]
			}
		}
	}
}

func flushBuffer(file *os.File, buffer []WeatherData) {
	for _, data := range buffer {
		line, _ := json.Marshal(data)
		fmt.Fprintln(file, string(line))
	}
}

func main() {
	apiKey := os.Getenv("OWM_API_KEY")
	if apiKey == "" {
		log.Fatal("OWM_API_KEY environment variable is required")
	}

	log.Println("Starting weather data collector...")
	ch := collectWeather(apiKey, 10*time.Minute)
	batchWriter(ch, 5, 10*time.Second)
}
