package com.voiceorder.orderservice;

import static io.grpc.MethodDescriptor.generateFullMethodName;

/**
 */
@javax.annotation.Generated(
    value = "by gRPC proto compiler (version 1.58.0)",
    comments = "Source: voice_service.proto")
@io.grpc.stub.annotations.GrpcGenerated
public final class VoiceServiceGrpc {

  private VoiceServiceGrpc() {}

  public static final java.lang.String SERVICE_NAME = "voiceorder.orderservice.VoiceService";

  // Static method descriptors that strictly reflect the proto.
  private static volatile io.grpc.MethodDescriptor<com.voiceorder.orderservice.VoiceRequest,
      com.voiceorder.orderservice.VoiceResponse> getProcessVoiceMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "ProcessVoice",
      requestType = com.voiceorder.orderservice.VoiceRequest.class,
      responseType = com.voiceorder.orderservice.VoiceResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<com.voiceorder.orderservice.VoiceRequest,
      com.voiceorder.orderservice.VoiceResponse> getProcessVoiceMethod() {
    io.grpc.MethodDescriptor<com.voiceorder.orderservice.VoiceRequest, com.voiceorder.orderservice.VoiceResponse> getProcessVoiceMethod;
    if ((getProcessVoiceMethod = VoiceServiceGrpc.getProcessVoiceMethod) == null) {
      synchronized (VoiceServiceGrpc.class) {
        if ((getProcessVoiceMethod = VoiceServiceGrpc.getProcessVoiceMethod) == null) {
          VoiceServiceGrpc.getProcessVoiceMethod = getProcessVoiceMethod =
              io.grpc.MethodDescriptor.<com.voiceorder.orderservice.VoiceRequest, com.voiceorder.orderservice.VoiceResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "ProcessVoice"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.voiceorder.orderservice.VoiceRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.voiceorder.orderservice.VoiceResponse.getDefaultInstance()))
              .setSchemaDescriptor(new VoiceServiceMethodDescriptorSupplier("ProcessVoice"))
              .build();
        }
      }
    }
    return getProcessVoiceMethod;
  }

  /**
   * Creates a new async stub that supports all call types for the service
   */
  public static VoiceServiceStub newStub(io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<VoiceServiceStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<VoiceServiceStub>() {
        @java.lang.Override
        public VoiceServiceStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new VoiceServiceStub(channel, callOptions);
        }
      };
    return VoiceServiceStub.newStub(factory, channel);
  }

  /**
   * Creates a new blocking-style stub that supports unary and streaming output calls on the service
   */
  public static VoiceServiceBlockingStub newBlockingStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<VoiceServiceBlockingStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<VoiceServiceBlockingStub>() {
        @java.lang.Override
        public VoiceServiceBlockingStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new VoiceServiceBlockingStub(channel, callOptions);
        }
      };
    return VoiceServiceBlockingStub.newStub(factory, channel);
  }

  /**
   * Creates a new ListenableFuture-style stub that supports unary calls on the service
   */
  public static VoiceServiceFutureStub newFutureStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<VoiceServiceFutureStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<VoiceServiceFutureStub>() {
        @java.lang.Override
        public VoiceServiceFutureStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new VoiceServiceFutureStub(channel, callOptions);
        }
      };
    return VoiceServiceFutureStub.newStub(factory, channel);
  }

  /**
   */
  public interface AsyncService {

    /**
     */
    default void processVoice(com.voiceorder.orderservice.VoiceRequest request,
        io.grpc.stub.StreamObserver<com.voiceorder.orderservice.VoiceResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getProcessVoiceMethod(), responseObserver);
    }
  }

  /**
   * Base class for the server implementation of the service VoiceService.
   */
  public static abstract class VoiceServiceImplBase
      implements io.grpc.BindableService, AsyncService {

    @java.lang.Override public final io.grpc.ServerServiceDefinition bindService() {
      return VoiceServiceGrpc.bindService(this);
    }
  }

  /**
   * A stub to allow clients to do asynchronous rpc calls to service VoiceService.
   */
  public static final class VoiceServiceStub
      extends io.grpc.stub.AbstractAsyncStub<VoiceServiceStub> {
    private VoiceServiceStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected VoiceServiceStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new VoiceServiceStub(channel, callOptions);
    }

    /**
     */
    public void processVoice(com.voiceorder.orderservice.VoiceRequest request,
        io.grpc.stub.StreamObserver<com.voiceorder.orderservice.VoiceResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getProcessVoiceMethod(), getCallOptions()), request, responseObserver);
    }
  }

  /**
   * A stub to allow clients to do synchronous rpc calls to service VoiceService.
   */
  public static final class VoiceServiceBlockingStub
      extends io.grpc.stub.AbstractBlockingStub<VoiceServiceBlockingStub> {
    private VoiceServiceBlockingStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected VoiceServiceBlockingStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new VoiceServiceBlockingStub(channel, callOptions);
    }

    /**
     */
    public com.voiceorder.orderservice.VoiceResponse processVoice(com.voiceorder.orderservice.VoiceRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getProcessVoiceMethod(), getCallOptions(), request);
    }
  }

  /**
   * A stub to allow clients to do ListenableFuture-style rpc calls to service VoiceService.
   */
  public static final class VoiceServiceFutureStub
      extends io.grpc.stub.AbstractFutureStub<VoiceServiceFutureStub> {
    private VoiceServiceFutureStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected VoiceServiceFutureStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new VoiceServiceFutureStub(channel, callOptions);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<com.voiceorder.orderservice.VoiceResponse> processVoice(
        com.voiceorder.orderservice.VoiceRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getProcessVoiceMethod(), getCallOptions()), request);
    }
  }

  private static final int METHODID_PROCESS_VOICE = 0;

  private static final class MethodHandlers<Req, Resp> implements
      io.grpc.stub.ServerCalls.UnaryMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ServerStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ClientStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.BidiStreamingMethod<Req, Resp> {
    private final AsyncService serviceImpl;
    private final int methodId;

    MethodHandlers(AsyncService serviceImpl, int methodId) {
      this.serviceImpl = serviceImpl;
      this.methodId = methodId;
    }

    @java.lang.Override
    @java.lang.SuppressWarnings("unchecked")
    public void invoke(Req request, io.grpc.stub.StreamObserver<Resp> responseObserver) {
      switch (methodId) {
        case METHODID_PROCESS_VOICE:
          serviceImpl.processVoice((com.voiceorder.orderservice.VoiceRequest) request,
              (io.grpc.stub.StreamObserver<com.voiceorder.orderservice.VoiceResponse>) responseObserver);
          break;
        default:
          throw new AssertionError();
      }
    }

    @java.lang.Override
    @java.lang.SuppressWarnings("unchecked")
    public io.grpc.stub.StreamObserver<Req> invoke(
        io.grpc.stub.StreamObserver<Resp> responseObserver) {
      switch (methodId) {
        default:
          throw new AssertionError();
      }
    }
  }

  public static final io.grpc.ServerServiceDefinition bindService(AsyncService service) {
    return io.grpc.ServerServiceDefinition.builder(getServiceDescriptor())
        .addMethod(
          getProcessVoiceMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              com.voiceorder.orderservice.VoiceRequest,
              com.voiceorder.orderservice.VoiceResponse>(
                service, METHODID_PROCESS_VOICE)))
        .build();
  }

  private static abstract class VoiceServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoFileDescriptorSupplier, io.grpc.protobuf.ProtoServiceDescriptorSupplier {
    VoiceServiceBaseDescriptorSupplier() {}

    @java.lang.Override
    public com.google.protobuf.Descriptors.FileDescriptor getFileDescriptor() {
      return com.voiceorder.orderservice.VoiceServiceProto.getDescriptor();
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.ServiceDescriptor getServiceDescriptor() {
      return getFileDescriptor().findServiceByName("VoiceService");
    }
  }

  private static final class VoiceServiceFileDescriptorSupplier
      extends VoiceServiceBaseDescriptorSupplier {
    VoiceServiceFileDescriptorSupplier() {}
  }

  private static final class VoiceServiceMethodDescriptorSupplier
      extends VoiceServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoMethodDescriptorSupplier {
    private final java.lang.String methodName;

    VoiceServiceMethodDescriptorSupplier(java.lang.String methodName) {
      this.methodName = methodName;
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.MethodDescriptor getMethodDescriptor() {
      return getServiceDescriptor().findMethodByName(methodName);
    }
  }

  private static volatile io.grpc.ServiceDescriptor serviceDescriptor;

  public static io.grpc.ServiceDescriptor getServiceDescriptor() {
    io.grpc.ServiceDescriptor result = serviceDescriptor;
    if (result == null) {
      synchronized (VoiceServiceGrpc.class) {
        result = serviceDescriptor;
        if (result == null) {
          serviceDescriptor = result = io.grpc.ServiceDescriptor.newBuilder(SERVICE_NAME)
              .setSchemaDescriptor(new VoiceServiceFileDescriptorSupplier())
              .addMethod(getProcessVoiceMethod())
              .build();
        }
      }
    }
    return result;
  }
}
