package com.datastructure.smartcanteen.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.math.BigDecimal;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("dish")
public class Dish extends BaseEntity {

    private Long categoryId;
    private String name;
    private BigDecimal price;
    private String image;
    private String description;
    private Integer status;
}
