FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY collector/go.mod collector/collector.go ./
RUN go build -o collector .

FROM alpine:3.19
RUN apk --no-cache add ca-certificates
WORKDIR /app
COPY --from=builder /app/collector .
CMD ["./collector"]
