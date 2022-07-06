package main

import "fmt"

type contactInfo struct {
	email   string
	zipCode int
}

type person struct {
	firstName string
	lastName  string
	contact   contactInfo
}

// another way to define struct
type person1 struct {
	firstName string
	lastName  string
	contactInfo
}

func main() {
	/*
		//alex := person{"Alex", "Anderson"}
		// #1 way to initialize struct , relies on order of fields defined in struct

		// harsh := person{firstName: "Harsh", lastName: "Jain"}
		// #2 another way to initialize a struct

		var alex person
		// #3 another way to initialize a struct, with nil/zero values to the
		// properties inside
		alex.firstName = "Alex"
		alex.lastName = "Anderson"
		fmt.Println(alex)
		fmt.Printf("%+v", alex)
	*/

	jim := person{
		firstName: "jim",
		lastName:  "party",
		contact: contactInfo{
			email:   "jim@gmail.com",
			zipCode: 560017,
		},
	}
	// jim is pointing to the value at some address

	jim.updateName("jimmy")
	// even after updating the name to jimmy we got print value as jim
	// but inside the function updateName we see that the value changed to jimmy
	// Go is a pass by value language
	// So when we send jim to updateName , go copies the value of jim to another address
	// and passes it to updateName receiver. Thus we are updating a copy of jim
	// inside updateName.
	//jim.print()

	jimPtr := &jim
	// jim is pointing to the actual value of the struct in memory
	// &jim gives the address to the value
	jimPtr.updateNamePtr("jimmy")
	jim.print()

	jim.updateNamePtr("jimmy new")
	// above will also work
	// shortcut to declaring pointer and sending to function
	// go allows us to call updateNamePtr with a pointer or with root type
	// go internally converts to pointer type
	jim.print()

	/*
			jim1 := person1{
			firstName: "jim1",
			lastName:  "party",
			contactInfo: contactInfo{
				email:   "jim@gmail.com",
				zipCode: 560017,
			},
		}
		fmt.Printf("%+v \n", jim1)
	*/
}

func (p person) print() {
	fmt.Printf("%+v \n", p)

}

func (p person) updateName(newFirstName string) {
	p.firstName = newFirstName
	//p.print()
}

func (pPtr *person) updateNamePtr(newFirstName string) {
	// above line *person is saying "a type of pointer which points at a person"

	(*pPtr).firstName = newFirstName
	// *pPtr gives the access to the value at address pPtr
}
