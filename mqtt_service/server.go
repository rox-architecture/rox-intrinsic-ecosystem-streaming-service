package main

import (
	"context"
	"errors"
	"fmt"
	rcpb "intrinsic/resources/proto/runtime_context_go_proto"
	"intrinsic/util/proto/protoio"
	"log"
	"net"
	"time"

	"eu.sotec/mqtt_service_proto"
	"google.golang.org/grpc"

	mqtt "github.com/eclipse/paho.mqtt.golang"
)

const (
	runtimeContextPath = "/etc/intrinsic/runtime_config.pb"
)

type MqttClientServer struct {
	mqtt_service_proto.UnimplementedMqttServiceServer

	Qos        uint32
	PublishTimeout time.Duration
	MqttClient mqtt.Client
}

func (s MqttClientServer) PublishMessage(ctx context.Context, in *mqtt_service_proto.MqttMessage) (*mqtt_service_proto.Empty, error) {
	token := s.MqttClient.Publish(in.Topic, byte(s.Qos), in.Retained, in.Message)
	
	if token.WaitTimeout(s.PublishTimeout) == false {
		log.Printf("Timeout: Failed to publish MQTT message.", in.Message, in.Topic)
		return nil, errors.New("Timeout: Failed to publish MQTT message.")
	}

	err := token.Error()
	if err != nil {
		log.Printf("Error publishing Message: %v", err)
		return nil, err
	}

	log.Printf("Published message '%s' to topic '%s'\n", in.Message, in.Topic)
	return &mqtt_service_proto.Empty{}, nil
}

func newMqttClientServer(config *mqtt_service_proto.MqttServiceConfig) *MqttClientServer {
	mqttClientServer := &MqttClientServer{}

	mqttClientServer.Qos = config.Qos
	mqttClientServer.PublishTimeout = time.Duration(config.PublishTimeout) * time.Millisecond

	// Setup mqtt client
	broker := fmt.Sprintf("tcp://%s:%d", config.Hostname, config.Port)
	clientID := "flowstate_mqtt_service"

	opts := mqtt.NewClientOptions()
	opts.AddBroker(broker)
	opts.SetClientID(clientID)
	opts.SetConnectRetry(true)
	opts.SetAutoReconnect(true)
	opts.SetConnectRetryInterval(5 * time.Second)

	if config.Username != nil && config.Password != nil {
		opts.SetUsername(*config.Username)
		opts.SetPassword(*config.Password)
	}

	opts.SetOnConnectHandler(func(c mqtt.Client) {
		log.Println("Successfully connected to the Mqtt Broker")
	})

	opts.SetConnectionLostHandler(func(c mqtt.Client, err error) {
		log.Printf("Connection to Broker lost: %v\n", err)
	})

	client := mqtt.NewClient(opts)
	mqttClientServer.MqttClient = client

	go func() {
		if token := client.Connect(); token.Wait() && token.Error() != nil {
			log.Fatalf("Something Went Wrong: %v", token.Error())
		}
	}()

	return mqttClientServer
}

func readRuntimeContext() (*rcpb.RuntimeContext, *mqtt_service_proto.MqttServiceConfig) {
	rc := new(rcpb.RuntimeContext)
	err := protoio.ReadBinaryProto(runtimeContextPath, rc)
	if err != nil {
		log.Fatalf("Failed to read runtime context: %v", err)
	}

	// reading config from the runtime config
	config := &mqtt_service_proto.MqttServiceConfig{}
	err = rc.Config.UnmarshalTo(config)
	if err != nil {
		log.Fatalf("was not able to unmarshal the service config: %v", config)
	}

	return rc, config
}

func main() {
	log.Println("Starting mqtt_service")

	rc, config := readRuntimeContext()
	listen, err := net.Listen("tcp", fmt.Sprintf(":%d", rc.GetPort()))
	if err != nil {
		log.Fatalf("Faild to listen at tcp Port: %v", err)
	}
	log.Printf("grpc server listening at %v", listen.Addr())

	server := grpc.NewServer()
	mqttClientServer := newMqttClientServer(config)
	mqtt_service_proto.RegisterMqttServiceServer(server, mqttClientServer)

	err = server.Serve(listen)
	if err != nil {
		mqttClientServer.MqttClient.Disconnect(255)
		log.Fatalf("Error in grpc server: %v", err)
	}
}
