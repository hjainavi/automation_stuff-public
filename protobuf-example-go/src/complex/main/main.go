package main

import (
	"fmt"

	"complex"

	"github.com/golang/protobuf/descriptor"
	"github.com/golang/protobuf/proto"
	"google.golang.org/protobuf/reflect/protoreflect"
)

func main() {
	doComplex()
}

func convert(m descriptor.Message) descriptor.Message {
	return m
}

func doComplex() {
	cm := complex.ComplexMessage{
		OneDummy: &complex.DummyMessage{
			Id:   proto.Int32(1),
			Name: proto.String("First message"),
		},
		MultipleDummy: []*complex.DummyMessage{
			&complex.DummyMessage{
				Id:   proto.Int32(2),
				Name: proto.String("Second message"),
			},
			&complex.DummyMessage{
				Id:   proto.Int32(3),
				Name: proto.String("Third message"),
			},
		},
		TwoMultipleDummy: []*complex.DummyMessage{},
		//TwoDummy:         &complex.DummyMessage{},
	}
	fmt.Println(cm)
	msg := proto.MessageReflect(&cm)
	msg.Range(func(fd protoreflect.FieldDescriptor, v protoreflect.Value) bool {
		//fmt.Println(fd.Cardinality().GoString(), fd.Name(), fd.Kind().GoString(), v.IsValid())
		if v.IsValid() && fd.Cardinality().GoString() == "Optional" {
			fmt.Println(fd.Name())
			abc := v.Message()
			fmt.Println(abc.Descriptor())
			//fmt.Println(convert(dynamicpb.NewMessage(v.Message().Descriptor())))
		}
		return true
	})

}
