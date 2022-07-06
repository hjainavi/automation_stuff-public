package main

import (
	"fmt"
	"os"

	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

type Product struct {
	gorm.Model
	Code  string
	Price uint
}

var dbLocal *gorm.DB

func GetDb() *gorm.DB {
	isThere := dbLocal != nil
	if isThere {
		return dbLocal
	}
	fmt.Println("got new conn")
	dbLocal, err := gorm.Open(sqlite.Open("test.db"), &gorm.Config{})
	if err != nil {
		panic("failed to connect database")
	}
	sqliteDB, _ := dbLocal.DB()
	sqliteDB.SetMaxOpenConns(4)
	return dbLocal
}

func main() {
	defer os.Remove("test.db")
	fmt.Println("test")
	db := GetDb()
	db2 := GetDb()
	// Migrate the schema
	db.AutoMigrate(&Product{})

	// Create
	db.Create(&Product{Code: "D42", Price: 100})

	var prod1 Product
	db2.First(&prod1, 1)
	// Read
	var product Product
	db.First(&product, 1)                 // find product with integer primary key
	db.First(&product, "code = ?", "D42") // find product with code D42

	// Update - update product's price to 200
	db.Model(&product).Update("Price", 200)
	// Update - update multiple fields
	db.Model(&product).Updates(Product{Price: 200, Code: "F42"}) // non-zero fields
	db.Model(&product).Updates(map[string]interface{}{"Price": 200, "Code": "F42"})

	// Delete - delete product
	db.Delete(&product, 1)
}
