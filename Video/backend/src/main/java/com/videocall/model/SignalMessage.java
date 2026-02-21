package com.videocall.model;

public class SignalMessage {
    private String type; // "offer", "answer", "ice-candidate"
    private String from;
    private String to;
    private Object data;

    public SignalMessage() {}

    public SignalMessage(String type, String from, String to, Object data) {
        this.type = type;
        this.from = from;
        this.to = to;
        this.data = data;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public String getFrom() {
        return from;
    }

    public void setFrom(String from) {
        this.from = from;
    }

    public String getTo() {
        return to;
    }

    public void setTo(String to) {
        this.to = to;
    }

    public Object getData() {
        return data;
    }

    public void setData(Object data) {
        this.data = data;
    }
}
